import gc
import sys

import constants
import machine
import utime


def active_today():
    """
    Is the timer active this weekday?
    """
    from times_utils import get_active_days
    active_days = get_active_days()
    del get_active_days
    del sys.modules['times_utils']
    gc.collect()

    today = utime.localtime()[6]
    print('Today:', today, 'active_days:', active_days)
    return today in active_days


def update_power_timer(power_timer):
    """
    Plan next switching point.
    """

    print('\ntimer scheduled in sec:', power_timer.timer_in_sec)
    if 0 <= power_timer.timer_in_sec < 60:
        print('Skip power timer update just <1min, before shot.')
        return

    from rtc import get_rtc_value
    from times_utils import get_next_timer
    from timezone import localtime_isoformat

    power_timer.last_update = localtime_isoformat(sep=' ')

    if power_timer.active is None:
        power_timer.active = get_rtc_value(key=constants.POWER_TIMER_ACTIVE_KEY, default=True)

    if power_timer.today_active is None:
        power_timer.today_active = active_today()

    if not power_timer.active:
        print('Not active -> do not schedule: %s' % power_timer)
        power_timer.timer.deinit()
        return

    if not power_timer.today_active:
        print('Not active today -> do not schedule: %s' % power_timer)
        power_timer.timer.deinit()
        return

    turn_on, next_timer_epoch = get_next_timer()
    if next_timer_epoch is None:
        print('No timer to schedule')
        power_timer.timer.deinit()
        return

    print('new....:', turn_on, next_timer_epoch)
    print('current:', power_timer.turn_on, power_timer.next_timer_epoch)
    if turn_on == power_timer.turn_on and abs(next_timer_epoch - power_timer.next_timer_epoch) < 60:
        print('Timer scheduled in the past -> nothing to update, ok')
        return

    power_timer.turn_on, power_timer.next_timer_epoch = turn_on, next_timer_epoch

    timer_in_sec = power_timer.timer_in_sec
    assert timer_in_sec > 0, 'negative timer ?!?'

    period = timer_in_sec * 1000

    print('Schedule with %i ms: %s' % (period, power_timer))
    power_timer.timer.init(
        period=period,
        mode=machine.Timer.ONE_SHOT,
        callback=power_timer._timer_callback
    )
