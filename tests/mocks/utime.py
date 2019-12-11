"""
    http://docs.micropython.org/en/latest/library/utime.html
    https://github.com/micropython/micropython/blob/master/ports/esp8266/modutime.c
"""
import calendar as _calendar
import time as _time


def localtime(sec=0):
    """
    http://docs.micropython.org/en/latest/library/utime.html#utime.localtime
    year, month, mday, hour, minute, second, weekday, yearday
    """
    sec += _calendar.timegm((2000, 1, 1, 0, 0, 0, 5, 1))  # micropython utime.localtime(0)
    struct_time = _time.gmtime(sec)
    return (
        struct_time.tm_year,
        struct_time.tm_mon,
        struct_time.tm_mday,
        struct_time.tm_hour,
        struct_time.tm_min,
        struct_time.tm_sec,
        struct_time.tm_wday,
        struct_time.tm_yday,
    )


def mktime(tuple_time):
    sec = _calendar.timegm(tuple_time)
    sec -= _calendar.timegm((2000, 1, 1, 0, 0, 0, 5, 1))  # micropython utime.localtime(0)
    return sec
