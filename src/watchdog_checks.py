import gc

import constants
import uerrno
import usocket
import utime
from reset import ResetDevice


def reset(reason):
    print('Watchdog reset reason: %s' % reason)
    from rtc import incr_rtc_count
    incr_rtc_count(key=constants.RTC_KEY_WATCHDOG_COUNT)
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
            # Web server not running, because we can bind the address
            return True
    finally:
        sock.close()


def check(context):
    gc.collect()
    try:
        if utime.time() - context.watchdog_last_feed_epoch > constants.WATCHDOG_TIMEOUT:
            reset(reason='Watchdog feed timeout')

        if can_bind_web_server_port():
            reset(reason='Web Server down')

        if utime.time() - context.ntp_last_sync_epoch > constants.NTP_LOST_SYNC_DEFAULT_SEC:
            reset(reason='NTP sync lost')

    except MemoryError as e:
        context.watchdog.garbage_collection()
        reset(reason='Memory error: %s' % e)

    gc.collect()
