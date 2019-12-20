

import gc

import constants
import micropython
import uerrno
import usocket
import utime
from micropython import const

_MIN_FREE = const(2 * 1024)


def reset(reason):
    print('Watchdog reset reason: %s' % reason)
    from rtc import incr_rtc_count
    incr_rtc_count(key=constants.RTC_KEY_WATCHDOG_COUNT)
    from reset import ResetDevice
    ResetDevice(reason=reason).reset()


def can_bind_web_server_port():
    server_address = (constants.WEBSERVER_HOST, constants.WEBSERVER_PORT)
    sock = usocket.socket()
    try:
        sock.settimeout(1)
        try:
            sock.bind(server_address)
        except OSError as e:
            # If webserver is running:
            # [Errno 98] EADDRINUSE
            if e.args[0] == uerrno.EADDRINUSE:
                return False
        else:
            print('ERROR: Web server not running! (Can bind to %s:%i)' % server_address)
            return True
    finally:
        sock.close()


def check(context):
    micropython.mem_info()

    gc.collect()
    # gc.threshold(gc.mem_free() // 4 + gc.mem_alloc())

    micropython.mem_info()

    try:
        if gc.mem_free() < _MIN_FREE:
            reset(reason='RAM full')

        if utime.time() - context.watchdog_last_feed > constants.WATCHDOG_TIMEOUT:
            reset(reason='Feed timeout')

        from wifi import ensure_connection
        if ensure_connection(context) is not True:
            reset(reason='No Wifi connection')

        if can_bind_web_server_port():
            reset(reason='Web Server down')

        from power_timer import update_power_timer
        if update_power_timer(context) is not True:
            reset(reason='Update power timer error')

        from ntp import ntp_sync
        if ntp_sync(context) is not True:
            reset(reason='NTP sync error')
    except MemoryError as e:
        reset(reason='Memory error: %s' % e)

    gc.collect()
