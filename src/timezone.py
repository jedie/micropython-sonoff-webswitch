"""
    timezone utilities
    ~~~~~~~~~~~~~~~~~~

    http://docs.micropython.org/en/latest/library/utime.html?highlight=datetime#utime.localtime
    year, month, mday, hour, minute, second, weekday, yearday
"""
import gc
import sys

import utime
from micropython import const

_TIMEZONE_PY_CFG_NAME = 'timezone'
_DEFAULT_OFFSET_H = const(0)


def save_timezone(offset_h):
    from config_files import save_py_config
    save_py_config(module_name=_TIMEZONE_PY_CFG_NAME, value=offset_h)

    del save_py_config
    del sys.modules['config_files']
    gc.collect()


def restore_timezone():
    from config_files import restore_py_config
    offset_h = restore_py_config(module_name=_TIMEZONE_PY_CFG_NAME, default=_DEFAULT_OFFSET_H)

    del restore_py_config
    del sys.modules['config_files']
    gc.collect()
    return offset_h


def localtime_isoformat(sep='T', dt=None, epoch=None, offset_h=None, add_offset=False):
    """
    dt = tuple from utime.localtime() and not from: machine.RTC().datetime() !
    """
    # dt = (year, month, mday, hour, minute, second, weekday, yearday)
    if dt is None:
        dt = utime.localtime(epoch)

    if not add_offset:
        return '%i-%02i-%02i%s%02i:%02i:%02i' % (dt[:3] + (sep,) + dt[3:6])

    if offset_h is None:
        offset_h = restore_timezone()

    return '%i-%02i-%02i%s%02i:%02i:%02i%s%02i:00' % (
        dt[:3] + (sep,) + dt[3:6] + ('+' if offset_h >= 0 else '-',) + (abs(offset_h),)
    )


def get_local_epoch():
    return utime.mktime(
        utime.localtime()  # year, month, mday, hour, minute, second, weekday, yearday
    ) + (
        abs(
            restore_timezone() * 60 * 60  # offset in sec can be positive and negative!
        )  # convert via abs() to a positive value
    )
    #
    # in steps, it looks like:
    #
    # offset_sec = abs(restore_timezone() * 60 * 60)
    #
    # # year, month, mday, hour, minute, second, weekday, yearday
    # utc_time_tuple = utime.localtime()
    # utc_now_epoch = utime.mktime(utc_time_tuple)
    #
    # local_epoch = utc_now_epoch + offset_sec
    # return local_epoch
