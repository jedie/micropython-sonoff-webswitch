import gc
import sys

import constants
import machine
import utime as time


def active_today():
    """
    Is the timer active this weekday?
    """
    from times_utils import get_active_days
    active_days = get_active_days()
    del get_active_days
    del sys.modules['times_utils']
    gc.collect()

    today = time.localtime()[6]
    print('Today:', today)
    return today in active_days


def update_power_timer(power_timer):
    """
    Plan next switching point.
    """
    power_timer.timer.deinit()

    from rtc import get_rtc_value, rtc_isoformat
    from times_utils import get_ms_until_next_timer

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
