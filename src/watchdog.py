import gc
import sys

import constants
import machine
import uerrno as errno
import usocket as socket
import utime as time
from rtc_memory import rtc_memory

_CHECK_PERIOD = const(50 * 1000)  # 50 sec

rtc = machine.RTC()

# get reset info form RTC RAM:
reset_count = rtc_memory.d.get(constants.RTC_KEY_WATCHDOG_COUNT, 0)
reset_reason = rtc_memory.d.get(constants.RTC_KEY_RESET_REASON)


def reset(reason):
    print('Watchdog reset reason: %s' % reason)

    # Save reason in RTC RAM:
    rtc_memory.save(data={constants.RTC_KEY_RESET_REASON: reason})

    for no in range(5, 1, -1):
        print('Watchdog: Hard reset device in %i sec...' % no)
        time.sleep(1)

    # Save reset count in RTC RAM:
    rtc_memory.incr_rtc_count(key=constants.RTC_KEY_WATCHDOG_COUNT)

    machine.reset()
    time.sleep(1)
    sys.exit()


def can_bind_web_server_port():
    server_address = (constants.WEBSERVER_HOST, constants.WEBSERVER_PORT)
    sock = socket.socket()
    try:
        sock.settimeout(1)
        try:
            sock.bind(server_address)
        except OSError as e:
            # If webserver is running:
            # [Errno 98] EADDRINUSE
            if e.args[0] == errno.EADDRINUSE:
                return False
        else:
            print('ERROR: Web server not running! (Can bind to %s:%i)' % server_address)
            return True
    finally:
        sock.close()


class Watchdog:
    last_check = 0
    check_count = 0

    timer = machine.Timer(-1)

    def __init__(self, wifi):
        self.wifi = wifi

        print('Start Watchdog period timer')
        self.timer.deinit()
        self.timer.init(
            period=_CHECK_PERIOD,
            mode=machine.Timer.PERIODIC,
            callback=self._timer_callback
        )

    def _timer_callback(self, timer):
        gc.collect()

        if not self.wifi.is_connected:
            self.wifi.ensure_connection()

        last_connection = time.time() - self.wifi.connected_time
        if last_connection > constants.WIFI_TIMEOUT:
            reset('WiFi timeout')

        if can_bind_web_server_port():
            reset('Web Server down')

        self.check_count += 1
        self.last_check = rtc.datetime()

    def deinit(self):
        self.timer.deinit()

    def __str__(self):
        return (
            'Watchdog -'
            ' last check: %s,'
            ' check count: %s,'
            ' reset count: %s,'
            ' last reset reason: %s'
        ) % (
            self.last_check, self.check_count,
            reset_count, reset_reason
        )
