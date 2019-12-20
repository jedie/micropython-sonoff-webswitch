"""
    Note: The device name will also be used as DHCP hostname!
"""

# import sys

import machine
import uos
import ure

_CFG_KEY = 'device_name'


def get_default_name():
    return '%s-%s' % (
        uos.uname().nodename,
        ''.join(['%02x' % char for char in reversed(machine.unique_id())])
    )


def save_device_name(name):
    new_name = ure.sub('[^A-Za-z0-9_-]+', '-', name).strip('-_')  # noqa
    if name != new_name:
        raise ValueError(new_name)

    from config_files import save_json_config
    save_json_config(key=_CFG_KEY, cfg=name)
    # del save_json_config
    # del sys.modules['config_files']


def get_device_name():
    from config_files import get_json_config
    name = get_json_config(key=_CFG_KEY)
    if not name:
        return get_default_name()
    return name
