"""
    Test device name functions on device
"""

from device_name import get_device_name, save_device_name


def run_all_device_name_tests():
    save_device_name('Test-1')
    assert get_device_name() == 'Test-1'

    try:
        save_device_name('Foo § Bar')
    except ValueError as new_name:
        assert str(new_name) == 'Foo-Bar'
    else:
        raise AssertionError('ValueError not raised')

    try:
        save_device_name('_aäoöuü Cool!')
    except ValueError as new_name:
        assert str(new_name) == 'a-o-u-Cool'
    else:
        raise AssertionError('ValueError not raised')


if __name__ == '__main__':
    print('Run tests on device...')
    import sys
    sys.modules.clear()

    import gc
    gc.collect()

    origin_device_name = get_device_name()
    try:
        run_all_device_name_tests()
    finally:
        if origin_device_name is not None:
            save_device_name(origin_device_name)

    print('OK')
