import constants
import machine


def update_power_timer(power_timer):
    """
    Plan next switching point.
    """
    from rtc import get_rtc_value, rtc_isoformat
    from times_utils import get_ms_until_next_timer

    power_timer.timer.deinit()

    if power_timer.active is None:
        power_timer.active = get_rtc_value(key=constants.POWER_TIMER_ACTIVE_KEY, default=True)

    power_timer.turn_on, power_timer.next_time, power_timer.next_time_ms = get_ms_until_next_timer(
        current_time=machine.RTC().datetime()[4:6]
    )

    power_timer.last_update = rtc_isoformat(sep=' ')

    print('Schedule: %s' % power_timer)

    if power_timer.turn_on is None:
        return

    power_timer.timer.init(
        period=power_timer.next_time_ms,
        mode=machine.Timer.ONE_SHOT,
        callback=power_timer._timer_callback
    )
