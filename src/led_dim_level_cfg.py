
import sys

from pins import Pins

_LED_DIM_LEVEL_PY_CFG_NAME = 'dim_level'


def set_power_led_level(dim_level):
    Pins.power_led.set_dim_level(dim_level=dim_level)

    from config_files import save_py_config
    save_py_config(module_name=_LED_DIM_LEVEL_PY_CFG_NAME, value=dim_level)

    del save_py_config
    del sys.modules['config_files']


def restore_power_led_level():
    from config_files import restore_py_config
    dim_level = restore_py_config(module_name=_LED_DIM_LEVEL_PY_CFG_NAME, default=0)

    del restore_py_config
    del sys.modules['config_files']

    Pins.power_led.set_dim_level(dim_level=dim_level)

    return dim_level
