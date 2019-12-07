import gc
import sys

import constants
import machine
import utime as time


def get_active_days():
    from rtc import get_rtc_value
    active_days = get_rtc_value(key=constants.POWER_TIMER_WEEKDAYS_KEY, default=list(range(7)))
    del get_rtc_value
    del sys.modules['rtc']
    gc.collect()
    return active_days


def active_today():
    """
    Is the timer active this weekday?
    """
    active_days = get_active_days()
    today = time.localtime()[6]
    return today in active_days


def update_power_timer(power_timer):
    """
    Plan next switching point.
    """
    from rtc import get_rtc_value, rtc_isoformat
    from times_utils import get_ms_until_next_timer

    power_timer.timer.deinit()

    if power_timer.active is None:
        power_timer.active = get_rtc_value(key=constants.POWER_TIMER_ACTIVE_KEY, default=True)

    if power_timer.today_active is None:
        power_timer.today_active = active_today()

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
