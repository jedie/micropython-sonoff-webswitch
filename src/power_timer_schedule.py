import gc
import sys

import constants
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
    Sets relay switch on/off on schedule and manual override.
    """
    from timezone import localtime_isoformat

    power_timer.last_update = localtime_isoformat(sep=' ')

    print('\nUpdate power timer at', power_timer.last_update)

    from rtc import get_dict_from_rtc
    from times_utils import get_next_timer

    rtc_memory_dict = get_dict_from_rtc()
    del get_dict_from_rtc
    del sys.modules['rtc']
    gc.collect()

    power_timer.active = rtc_memory_dict.get(constants.POWER_TIMER_ACTIVE_KEY, True)

    manual_overwrite = rtc_memory_dict.get(constants.RTC_KEY_MANUAL_OVERWRITE, 0)
    current_state = rtc_memory_dict.get(constants.RTC_KEY_MANUAL_OVERWRITE_TYPE)

    del rtc_memory_dict
    gc.collect()

    # def epoch2clock(epoch):
    #     if epoch is None:
    #         return '-'
    #     return '%s (%i)' % (
    #         ':'.join(['%02i' % i for i in utime.localtime(epoch)[3:5]]),
    #         epoch
    #     )
    #
    # print('manual overwrite:', epoch2clock(manual_overwrite), current_state)

    if power_timer.today_active is None:
        power_timer.today_active = active_today()

    if power_timer.active and power_timer.today_active:
        # Update power timer state
        last_timer_epoch, power_timer.turn_on, power_timer.next_timer_epoch = get_next_timer()
        if last_timer_epoch is None:
            print('No timer scheduled')
        else:
            # print('last timer......:', epoch2clock(last_timer_epoch))

            if current_state is None or manual_overwrite < last_timer_epoch:
                print('Set state from timer')
                # Note:
                # The current power state is the **opposite** of the next one.
                # In other words: If the **next** timer will "turn on" (==True) then we are
                # now in a "OFF" phase ;)
                current_state = not power_timer.turn_on

    # print('next timer......:',
    #       epoch2clock(power_timer.next_timer_epoch),
    #       'ON' if power_timer.turn_on else 'OFF')

    if current_state is None:
        # No timer to scheduled and no manual overwrite
        return

    from pins import Pins
    if current_state:
        print('Switch on')
        Pins.relay.on()
    else:
        print('Switch off')
        Pins.relay.off()
