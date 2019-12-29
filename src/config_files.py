"""
    JSON-/PY-files config
    ~~~~~~~~~~~~~~~~~~~~~

    IMPORTANT: Use "py config files" only for validated data!
    IMPORTANT: It enables code injections!

    https://forum.micropython.org/viewtopic.php?f=2&t=7386
"""
import gc
import sys

import constants


def get_json_config(key):
    from ujson import load
    try:
        with open(constants.JSON_CFG_FILE_PATTERN % key, 'r') as f:
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
    with open(constants.JSON_CFG_FILE_PATTERN % key, 'w') as f:
        dump({key: cfg}, f)

    gc.collect()


def restore_py_config(module_name, default=None):
    """
    IMPORTANT: Enables code injections! So use with care!
    """
    module_name = constants.PY_MODULE_NAME_PATTERN % module_name
    if __debug__:
        print('restore py config', module_name)
    try:
        module = __import__(module_name, None, None)
    except ImportError as e:
        if __debug__:
            print('Import error:', e)
            # e.g: py file not created, yet.
        return default
    except SyntaxError:
        print('Syntax error in:', module_name)
        import os
        os.remove(module_name + '.py')
        return default

    value = getattr(module, 'value', default)

    # Important to remove from module cache, to get a fresh value on next import ;)
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

    file_name = constants.PY_FILE_PATTERN % module_name

    if __debug__:
        print('save py config', module_name, value, file_name)

    with open(file_name, 'w') as f:
        print('Store in %r: %r' % (file_name, value))
        if isinstance(value, int):
            f.write('from micropython import const\n')
            f.write('value = const(%s)' % repr(value))
        else:
            f.write('value = %s' % repr(value))

    gc.collect()
