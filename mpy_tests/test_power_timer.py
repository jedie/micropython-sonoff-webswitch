"""
    Tests power timer on device
"""
from power_timer import PowerTimer


def run_all_power_timer_tests():
    print('test not active...', end=' ')
    power_timer = PowerTimer()
    result = power_timer.info_text()
    assert result == 'Power timer is deactivated. (Last update: None)', result
    result = str(power_timer)
    assert result == (
        'last_update=None, next_timer_epoch=None,'
        ' turn_on=None, active=None, today_active=None'
    ), result
    print('OK')

    print('test active...', end=' ')
    power_timer.active = True
    power_timer.today_active = True
    result = power_timer.info_text()
    assert result == 'No switch scheduled. (Last update: None)', result
    result = str(power_timer)
    assert result == (
        'last_update=None, next_timer_epoch=None,'
        ' turn_on=None, active=True, today_active=True'
    ), result
    print('OK')


if __name__ == '__main__':
    print('Run tests on device...')
    import sys
    sys.modules.clear()

    import gc
    gc.collect()

    run_all_power_timer_tests()
    print('OK')
