import gc
import sys


def reset(reason):
    from reset import ResetDevice
    ResetDevice(reason=reason).reset()


async def periodical_tasks(context):
    """
    Periodical tasks, started from webswitch.WebServer.feed_watchdog
    """
    if context.ntp_last_sync_epoch > 0:  # A NTP sync was successful in the past

        # Sets relay switch on/off on schedule and manual override:

        from power_timer import update_power_timer
        update_power_timer(context)

        del update_power_timer
        del sys.modules['power_timer']
        gc.collect()

    # Ensure that the device is connected to the WiFi:

    from wifi import ensure_connection
    is_connected = ensure_connection(context)

    del ensure_connection
    del sys.modules['wifi']
    gc.collect()

    if is_connected:
        # Sync the RTC time via NTP:

        from ntp import ntp_sync
        ntp_sync(context)

        del ntp_sync
        del sys.modules['ntp']
        gc.collect()
