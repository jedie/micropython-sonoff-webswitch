"""
    Tests config files on device
"""
import os

from config_files import get_json_config, restore_py_config, save_json_config, save_py_config


def test_json_config():
    try:
        assert get_json_config(key='test') is None

        save_json_config(key='test', cfg=123)
        assert get_json_config(key='test') == 123

        save_json_config(key='test', cfg={'bar': 1})
        save_json_config(key='test', cfg={'bar': 1})  # skip save?
        assert get_json_config(key='test') == {'bar': 1}
    finally:
        os.remove('_config_test.json')


def test_py_config():
    try:
        save_py_config(module_name='test', value=1)
        assert restore_py_config(module_name='test') == 1

        save_py_config(module_name='test', value=2)
        save_py_config(module_name='test', value=2)  # skip save?
        assert restore_py_config(module_name='test') == 2
    finally:
        os.remove('_config_test.py')


if __name__ == '__main__':
    print('Run tests on device...')
    import sys
    sys.modules.clear()

    import gc
    gc.collect()

    print('Run json config tests...')
    test_json_config()
    print('OK')

    print('Run py config tests...')
    test_py_config()
    print('OK')
