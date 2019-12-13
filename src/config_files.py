"""
    JSON-/PY-files config
    ~~~~~~~~~~~~~~~~~~~~~

    IMPORTANT: Use "py config files" only for validated data!
    IMPORTANT: It enables code injections!

    https://forum.micropython.org/viewtopic.php?f=2&t=7386
"""
import gc
import sys

_CFG_FILE_PREFIX = '_config_'

_JSON_CFG_FILE_PATTERN = _CFG_FILE_PREFIX + '%s.json'  # e.g.: _config_foobar.json

_PY_MODULE_NAME_PATTERN = _CFG_FILE_PREFIX + '%s'  # e.g.: _config_foobar
_PY_VALUE_ATTRIBUTE_NAME = 'value'
_PY_FILE_PATTERN = _CFG_FILE_PREFIX + '%s.py'  # e.g.: _config_foobar.py


def get_json_config(key):
    from ujson import load
    try:
        with open(_JSON_CFG_FILE_PATTERN % key, 'r') as f:
            return load(f)[key]
    except OSError:
        return  # e.g.: file not exists


def save_json_config(key, cfg):
    """
    Will create files like: 'config_{key}.json'
    """
    if cfg == get_json_config(key):
        print('Skip save json config: Already exists with same data.')
        return

    from ujson import dump
    with open(_JSON_CFG_FILE_PATTERN % key, 'w') as f:
        dump({key: cfg}, f)

    if get_json_config(key=key) != cfg:
        raise AssertionError('Json config verify error!')


def restore_py_config(module_name, default=None):
    """
    IMPORTANT: Enables code injections! So use with care!
    """
    module_name = _PY_MODULE_NAME_PATTERN % module_name
    try:
        module = __import__(module_name, None, None)
    except ImportError:
        # e.g: py file not created, yet.
        return default
    except SyntaxError:
        file_name = module_name + '.py'
        print('Syntax error in:', file_name)
        with open(file_name, 'r') as f:
            print(f.read())
        print('Remove file...')
        import os
        os.remove(file_name)
        return default

    value = getattr(module, _PY_VALUE_ATTRIBUTE_NAME, default)

    del module
    del sys.modules[module_name]
    gc.collect()
    return value


def save_py_config(module_name, value):
    """
    Will create files like: 'config_{key}.py'
    IMPORTANT: Enables code injections! So use with care!
    """
    if restore_py_config(module_name) == value:
        print('Skip save py config: Already exists with this value')
        return

    file_name = _PY_FILE_PATTERN % module_name
    with open(file_name, 'w') as f:
        print('Store in %r: %r' % (file_name, value))
        if isinstance(value, (int, float)):
            f.write('from micropython import const\n')
            f.write('%s = const(%r)' % (_PY_VALUE_ATTRIBUTE_NAME, value))
        else:
            f.write('%s = %r' % (_PY_VALUE_ATTRIBUTE_NAME, value))

    verify = restore_py_config(module_name)
    if verify != value:
        raise AssertionError('Py config verify error: %r != %r' % (verify, value))
