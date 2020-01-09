"""
    Note: The device name will also be used as DHCP hostname!
"""
import gc
import sys

import machine
import uos
import ure

_CFG_KEY = 'device_name'


def get_default_name():
    return '%s-%s' % (
        uos.uname().nodename,
        ''.join(['%02x' % char for char in reversed(machine.unique_id())])
    )


def save_device_name(server, name):
    new_name = ure.sub('[^A-Za-z0-9_-]+', '-', name).strip('-_')  # noqa
    if name != new_name:
        server.message = 'Error: Device name contains not allowed characters!'
        raise ValueError(new_name)

    if len(new_name) < 3:
        server.message = 'Error: New Device name is too short. Enter at leased 3 characters!'
        raise ValueError(new_name)

    from config_files import save_json_config
    save_json_config(key=_CFG_KEY, cfg=name)
    del save_json_config
    del sys.modules['config_files']
    gc.collect()

    server.message = 'Device name %r saved.' % new_name


def get_device_name():
    from config_files import get_json_config
    name = get_json_config(key=_CFG_KEY)
    if not name:
        name = get_default_name()

    del get_json_config
    del sys.modules['config_files']
    gc.collect()
    return name
