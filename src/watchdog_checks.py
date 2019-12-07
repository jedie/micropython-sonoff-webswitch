import gc

import constants
import uerrno as errno
import usocket as socket
import utime as time
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


def check(last_feed, wifi, check_callback):
    if gc.mem_free() < _MIN_FREE:
        reset(reason='RAM full')

    if not wifi.is_connected:
        wifi.ensure_connection()

    last_connection = time.time() - wifi.connected_time
    if last_connection > constants.WIFI_TIMEOUT:
        reset(reason='WiFi timeout')

    if can_bind_web_server_port():
        reset(reason='Web Server down')

    if time.time() - last_feed > constants.WATCHDOG_TIMEOUT:
        reset(reason='Feed timeout')

    check_callback()
