"""
    Tests power timer on device
"""
from power_timer import PowerTimer


def run_device_test():
    print('test not active...', end=' ')
    power_timer = PowerTimer()
    results = str(power_timer)
    assert results == 'Power timer is not active.', results
    print('OK')

    print('test active...', end=' ')
    power_timer.active = True
    results = str(power_timer)
    assert results == 'No switch scheduled. (Last update: None)', results
    print('OK')

    print('test schedule_next_switch()...', end=' ')
    power_timer.schedule_next_switch()
    power_timer.next_time_ms = 0
    results = str(power_timer)
    assert results == 'missed timer', results
    print('OK')


if __name__ == '__main__':
    print('Run tests on device...')
    import sys
    sys.modules.clear()

    import gc
    gc.collect()

    run_device_test()
    print('OK')
