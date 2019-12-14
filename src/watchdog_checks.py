import gc

import constants
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


def check(last_feed, wifi, check_callback):
    if gc.mem_free() < _MIN_FREE:
        reset(reason='RAM full')

    if not wifi.is_connected:
        wifi.ensure_connection()

    if wifi.connected_time is None:
        reset(reason='WiFi not connected')

    last_connection = utime.time() - wifi.connected_time
    if last_connection > constants.WIFI_TIMEOUT:
        reset(reason='WiFi timeout')

    if can_bind_web_server_port():
        reset(reason='Web Server down')

    if utime.time() - last_feed > constants.WATCHDOG_TIMEOUT:
        reset(reason='Feed timeout')

    check_callback()
