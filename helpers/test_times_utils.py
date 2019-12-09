"""
    Tests time utils on device

    see also pytests for hosts:
        tests/test_time_utils.py

    Note: Will overwrite existing saved timers!
"""


import uos as os
from times_utils import get_active_days, parse_timers, restore_timers, save_active_days, save_timers


def run_device_test():

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
        os.remove('timers.txt')
    except BaseException:
        pass
    results = tuple(restore_timers())
    assert results == (), results
    print('OK\n')

    print('test save_timers()...', end=' ')
    save_timers([
        ((6, 0), (7, 0)),
        ((19, 0), (22, 0))
    ])
    results = tuple(restore_timers())
    assert results == (
        ((6, 0), (7, 0)),
        ((19, 0), (22, 0))
    ), results
    print('OK\n')

    print('test not existing "timer_days.txt"...', end=' ')
    try:
        os.remove('timer_days.txt')
    except BaseException:
        pass
    results = tuple(get_active_days())
    assert results == (0, 1, 2, 3, 4, 5, 6), results
    print('OK\n')

    print('test save_active_days()...', end=' ')
    save_active_days(active_days=(0, 1, 2, 3, 4))
    results = tuple(get_active_days())
    assert results == (0, 1, 2, 3, 4), results
    print('OK\n')


if __name__ == '__main__':
    print('Run tests on device...')

    import sys
    sys.modules.clear()

    import gc
    gc.collect()

    run_device_test()
    print('OK\n')
