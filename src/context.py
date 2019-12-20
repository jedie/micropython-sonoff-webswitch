
class Context:
    power_timer_active = True
    power_timer_today_active = True
    power_timer_turn_on = None
    power_timer_next_timer = None  # epoch
    power_timer_last_update = None  # epoch
    power_timer_info_text = '???'

    wifi_last_update = None  # epoch
    wifi_first_connect_time = None  # epoch
    wifi_connected = 0
    wifi_not_connected = 0

    ntp_last_sync = None  # iso formatted string
    ntp_next_sync = 0  # epoch

    watchdog_last_check = None  # iso formatted string
    watchdog_last_feed = 0  # epoch
    watchdog_check_count = 0
    watchdog_reset_count = 0
    watchdog_last_reset_reason = 0

    minimal_modules = None
