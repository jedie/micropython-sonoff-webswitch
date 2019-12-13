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
