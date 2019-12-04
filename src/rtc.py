import sys

import machine
import ujson as json


def get_dict_from_rtc():
    """
    Restore dict via json from RTC RAM
    """
    rtc = machine.RTC().memory()
    if rtc:
        try:
            return json.loads(rtc)
        except ValueError as e:
            sys.print_exception(e)
            print('RTC memory:', rtc)

    return {}


def get_rtc_value(key, default=None):
    d = get_dict_from_rtc()
    return d.get(key, default)


def clear_rtc_dict():
    machine.RTC().memory(b'{}')


def update_rtc_dict(data):
    d = get_dict_from_rtc()
    d.update(data)
    machine.RTC().memory(json.dumps(d))


def incr_rtc_count(key):
    d = get_dict_from_rtc()
    count = d.get(key, 0) + 1
    update_rtc_dict(data={key: count})
    return count


def rtc_isoformat(sep='T'):
    dt = machine.RTC().datetime()
    return '%i-%02i-%02i%s%02i:%02i:%02i+00:00' % (dt[:3] + (sep,) + dt[4:7])


def rtc_later(time):
    dt = machine.RTC().datetime()
    return tuple(time) <= dt[4:6]


def rtc_in_time_range(time1, time2):
    dt = machine.RTC().datetime()
    return tuple(time1) <= dt[4:6] <= tuple(time2)


if __name__ == '__main__':
    print('RTC 1:', get_dict_from_rtc())
    count = incr_rtc_count(key='test')
    print('RTC memory test call count:', count)
    print('RTC 2:', get_dict_from_rtc())
    print(rtc_in_time_range((0, 0), (23, 59)))
    print(rtc_in_time_range((0, 0), (0, 1)))
