"""
    Test device name functions on device
"""

from device_name import get_device_name, save_device_name


class MockServer:
    message = None


mock_server = MockServer()


def run_all_device_name_tests():
    save_device_name(mock_server, 'Test-1')
    assert get_device_name() == 'Test-1'
    assert mock_server.message == "Device name 'Test-1' saved."

    try:
        save_device_name(mock_server, 'a')
    except ValueError as new_name:
        assert str(new_name) == 'a'
        assert mock_server.message == (
            'Error: New Device name is too short. Enter at leased 3 characters!'
        )
    else:
        raise AssertionError('ValueError not raised')

    try:
        save_device_name(mock_server, 'Foo § Bar')
    except ValueError as new_name:
        assert str(new_name) == 'Foo-Bar'
        assert mock_server.message == 'Error: Device name contains not allowed characters!'
    else:
        raise AssertionError('ValueError not raised')

    try:
        save_device_name(mock_server, '_aäoöuü Cool!')
    except ValueError as new_name:
        assert str(new_name) == 'a-o-u-Cool'
        assert mock_server.message == 'Error: Device name contains not allowed characters!'
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
            save_device_name(mock_server, origin_device_name)

    print('OK')
