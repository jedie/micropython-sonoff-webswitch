"""
    Tests time utils on device

    see also pytests for hosts:
        tests/test_time_utils.py

    Note: Will overwrite existing saved timers!
"""
import machine
import uos
import utime
from times_utils import (get_active_days, get_next_timer, human_timer_duration, parse_timers,
                         restore_timers, save_active_days, save_timers)
from timezone import localtime_isoformat


def epoch_info(epoch):
    year, month, mday, hour, minute, second, weekday, yearday = utime.localtime(epoch)
    return human_timer_duration(epoch), hour, minute, localtime_isoformat(epoch=epoch)


def assert_current_timer(reference):
    previous_epoch, turn_on, next_epoch = get_next_timer()
    text = '%i %s %02i:%02i %s -> %i %s %02i:%02i %s -> %s' % ((previous_epoch,) + epoch_info(
        previous_epoch) + (next_epoch, ) + epoch_info(next_epoch) + ('ON' if turn_on else 'OFF',))
    assert text == reference


def run_all_times_utils_tests():

    print('test parse_timers()...', end=' ')
    results = tuple(parse_timers('''
        0:00 - 1:00
        1:23 - 4:56
        19:00 - 20:00
        22:01 - 22:30
        23:12 - 23:59
    '''))
    assert results == (
        ((0, 0), (1, 0)),
        ((1, 23), (4, 56)),
        ((19, 0), (20, 0)),
        ((22, 1), (22, 30)),
        ((23, 12), (23, 59))
    ), results
    print('OK\n')

    print('test not existing "timers.txt"...', end=' ')
    try:
        uos.remove('_config_timers.py')
    except OSError:
        pass
    results = tuple(restore_timers())
    assert results == (), results
    print('OK\n')

    print('test not existing "timer_days.txt"...', end=' ')
    try:
        uos.remove('_config_timer_days.py')
    except OSError:
        pass
    results = tuple(get_active_days())
    assert results == (0, 1, 2, 3, 4, 5, 6), results
    print('OK\n')

    print('test save_active_days()...', end=' ')
    save_active_days(active_days=(0, 1, 2, 3, 4))
    results = tuple(get_active_days())
    assert results == (0, 1, 2, 3, 4), results
    print('OK\n')

    save_timers([])
    results = tuple(restore_timers())
    assert results == (), results
    assert get_next_timer() == (None, None, None)

    save_timers([
        ((6, 0), (7, 0)),
    ])
    results = tuple(restore_timers())
    assert results == (
        ((6, 0), (7, 0)),
    ), results

    rtc = machine.RTC()
    rtc.datetime((2000, 1, 2, 6, 0, 0, 0, 0))  # set RTC time: 2.1.2000 00:00:00
    assert_current_timer(  # Turn ON at 06:00
        '25200 -17 h 07:00 2000-01-01T07:00:00 -> 108000 6 h 06:00 2000-01-02T06:00:00 -> ON'
    )

    rtc.datetime((2000, 1, 2, 6, 5, 59, 59, 0))  # set RTC time: 2.1.2000 05:59:59
    assert_current_timer(  # Turn ON at 06:00
        '25200 -22 h 07:00 2000-01-01T07:00:00 -> 108000 1 sec 06:00 2000-01-02T06:00:00 -> ON'
    )

    rtc.datetime((2000, 1, 2, 6, 6, 0, 0, 0))  # set RTC time: 2.1.2000 06:00:00
    assert_current_timer(  # Turn ON at 06:00
        '108000 0 sec 06:00 2000-01-02T06:00:00 -> 111600 60 min 07:00 2000-01-02T07:00:00 -> OFF'
    )

    rtc.datetime((2000, 1, 2, 6, 6, 59, 59, 0))  # set RTC time: 2.1.2000 06:59:59
    assert_current_timer(  # Turn OFF at 07:00
        '108000 -59 min 06:00 2000-01-02T06:00:00 -> 111600 1 sec 07:00 2000-01-02T07:00:00 -> OFF'
    )

    rtc.datetime((2000, 1, 2, 6, 7, 0, 0, 0))  # set RTC time: 2.1.2000 07:00:00
    assert_current_timer(  # Turn ON next day at 06:00
        '111600 0 sec 07:00 2000-01-02T07:00:00 -> 194400 23 h 06:00 2000-01-03T06:00:00 -> ON'
    )

    save_timers([
        ((6, 0), (7, 0)),
        ((19, 30), (22, 30)),
    ])
    rtc.datetime((2000, 1, 2, 6, 0, 0, 0, 0))  # set RTC time: 2.1.2000 00:00:00
    assert_current_timer(  # Turn ON at 06:00
        '81000 -90 min 22:30 2000-01-01T22:30:00 -> 108000 6 h 06:00 2000-01-02T06:00:00 -> ON'
    )

    rtc.datetime((2000, 1, 2, 6, 7, 0, 1, 0))  # set RTC time: 2.1.2000 07:00:01
    assert_current_timer(  # Turn ON at 19:30
        '111600 -1 sec 07:00 2000-01-02T07:00:00 -> 156600 12 h 19:30 2000-01-02T19:30:00 -> ON'
    )

    rtc.datetime((2000, 1, 2, 6, 20, 12, 0, 0))  # set RTC time: 2.1.2000 20:12:00
    assert_current_timer(  # Turn OFF at 22:30
        '156600 -42 min 19:30 2000-01-02T19:30:00 -> 167400 2 h 22:30 2000-01-02T22:30:00 -> OFF'
    )

    rtc.datetime((2000, 1, 2, 6, 22, 30, 1, 0))  # set RTC time: 2.1.2000 22:30:01
    assert_current_timer(  # Turn ON next day at 06:00
        '167400 -1 sec 22:30 2000-01-02T22:30:00 -> 194400 7 h 06:00 2000-01-03T06:00:00 -> ON'
    )


if __name__ == '__main__':
    print('Run tests on device...')

    import sys
    sys.modules.clear()

    import gc
    gc.collect()

    timers = restore_timers()
    active_days = tuple(get_active_days())
    try:
        run_all_times_utils_tests()
    finally:
        if timers is not None:
            save_timers(timers)
        if active_days is None:
            save_active_days(active_days)

    print('OK\n')
