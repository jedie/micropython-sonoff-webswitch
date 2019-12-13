'''
    Tests power timer on device
'''
from power_timer import PowerTimer


def test_power_timer():
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

    print('test schedule_next_switch()...', end=' ')
    power_timer.schedule_next_switch()
    power_timer.timer.deinit()
    power_timer.next_timer_epoch = 0
    power_timer.last_update = 0
    result = power_timer.info_text()
    assert result == 'missed timer (Last update: 0)', result
    result = str(power_timer)
    assert result == (
        'last_update=0, next_timer_epoch=None,'
        ' turn_on=None, active=True, today_active=True'
    ), result
    print('OK')


if __name__ == '__main__':
    print('Run tests on device...')
    import sys
    sys.modules.clear()

    import gc
    gc.collect()

    test_power_timer()
    print('OK')
