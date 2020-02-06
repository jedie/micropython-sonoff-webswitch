import gc
import sys

import constants
import utime
from pins import Pins


def get_info_text(context):
    if not context.power_timer_active:
        return 'Power timer is deactivated.'

    if context.power_timer_today_active is False:
        return 'Power timer is not active today.'

    if context.power_timer_next_timer_epoch is None:
        return 'No switch scheduled.'

    # year, month, mday, hour, minute, second, weekday, yearday
    timer_hour, timer_min = utime.localtime(context.power_timer_next_timer_epoch)[3:5]
    from times_utils import human_timer_duration

    return 'Switch %s in %s at %02i:%02i h.' % (
        'on' if context.power_timer_turn_on else 'off',
        human_timer_duration(context.power_timer_next_timer_epoch),
        timer_hour, timer_min,
    )


def active_today():
    """
    Is the timer active this weekday?
    """
    from times_utils import get_active_days
    is_active_today = utime.localtime()[6] in get_active_days()
    del get_active_days
    del sys.modules['times_utils']
    gc.collect()

    return is_active_today


def update_power_timer(context):
    """
    Sets relay switch on/off on schedule and manual override.
    Called from tasks.periodical_tasks()
    """
    gc.collect()
    if __debug__:
        print('Update power timer:', utime.time())

    from times_utils import restore_timers
    context.power_timer_timers = restore_timers()
    del restore_timers
    del sys.modules['times_utils']
    gc.collect()

    from rtc import get_dict_from_rtc
    rtc_memory_dict = get_dict_from_rtc()

    context.power_timer_active = rtc_memory_dict.get(constants.POWER_TIMER_ACTIVE_KEY, True)

    manual_overwrite = rtc_memory_dict.get(constants.RTC_KEY_MANUAL_OVERWRITE, 0)
    current_state = rtc_memory_dict.get(constants.RTC_KEY_MANUAL_OVERWRITE_TYPE)
    if __debug__ and current_state:
        print('manual overwrite:', repr(current_state))

    del rtc_memory_dict
    del sys.modules['rtc']
    gc.collect()

    context.power_timer_today_active = active_today()

    if context.power_timer_active and context.power_timer_today_active:
        if __debug__:
            print('Update power timer state')
        from times_utils import get_current_timer
        last_timer_epoch, turn_on, context.power_timer_next_timer_epoch = get_current_timer(context)

        del get_current_timer
        del sys.modules['times_utils']
        gc.collect()

        context.power_timer_turn_on = turn_on

        if last_timer_epoch is None:
            if __debug__:
                print('No timer scheduled')
        else:
            if current_state is None or manual_overwrite < last_timer_epoch:
                if __debug__:
                    print('Set state from timer')
                # Note:
                # The current power state is the **opposite** of the next one.
                # In other words: If the **next** timer will "turn on" (==True) then we are
                # now in a "OFF" phase ;)
                current_state = not turn_on

    if current_state is None:
        if __debug__:
            print('No timer to scheduled and no manual overwrite')
    elif current_state:
        if __debug__:
            print('Switch on')
        Pins.relay.on()
    else:
        if __debug__:
            print('Switch off')
        Pins.relay.off()

    gc.collect()
