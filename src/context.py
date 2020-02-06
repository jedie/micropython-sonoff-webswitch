
class Context:
    power_timer_active = True
    power_timer_today_active = True
    power_timer_timers = None
    power_timer_turn_on = None
    power_timer_next_timer_epoch = None

    wifi_first_connect_epoch = None  # epoch
    wifi_last_connect_epoch = 0  # epoch
    wifi_connected = 0
    wifi_not_connected = 0

    ntp_last_sync_epoch = 0  # epoch
    ntp_next_sync_epoch = 0  # epoch

    watchdog_last_feed_epoch = 0  # epoch
    watchdog_check_count = 0
    watchdog_reset_count = 0
    watchdog_last_reset_reason = 0

    minimal_modules = None
