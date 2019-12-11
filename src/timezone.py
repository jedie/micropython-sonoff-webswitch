"""
    timezone utilities
    ~~~~~~~~~~~~~~~~~~

    http://docs.micropython.org/en/latest/library/utime.html?highlight=datetime#utime.localtime
    year, month, mday, hour, minute, second, weekday, yearday
"""

import utime
from micropython import const

_TIMEZONE_FILENAME = 'timezone.txt'
_DEFAULT_OFFSET_H = const(0)
_h2sec = const(60 * 60)


def datetime_shift(dt, offset_h):
    return utime.localtime(
        utime.mktime(dt) + (
            offset_h * _h2sec
        )
    )


def clock_time_shift(clock_time, offset_h):
    dt = datetime_shift(
        dt=(2000, 1, 2, clock_time[0], clock_time[1], 0, 6, 2),
        offset_h=offset_h
    )
    return dt[3], dt[4]


def save_timezone(offset_h):
    if restore_timezone() == offset_h:
        # Don't save if the same offset already exists
        return

    with open(_TIMEZONE_FILENAME, 'w') as f:
        f.write('%+i' % offset_h)


def restore_timezone():
    try:
        with open(_TIMEZONE_FILENAME, 'r') as f:
            try:
                return int(f.read())
            except ValueError:
                return _DEFAULT_OFFSET_H
    except OSError:
        print('File not exists: %r' % _TIMEZONE_FILENAME)
        return _DEFAULT_OFFSET_H
