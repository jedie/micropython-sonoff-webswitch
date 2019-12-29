import machine
import utime

from context import Context
from ntp import ntp_sync


def print_times():
    # year, month, day, weekday, hours, minutes, seconds, ???
    print('machine.RTC().datetime():', machine.RTC().datetime())

    # http://docs.micropython.org/en/latest/library/uutime.html#uutime.localtime
    # year, month, mday, hour, minute, second, weekday, yearday
    print('utime.localtime().......:', utime.localtime())


if __name__ == '__main__':
    context = Context
    ntp_sync(context)

    print_times()

    rtc = machine.RTC()
    rtc.datetime((2017, 8, 23, 1, 12, 48, 0, 0))  # set a specific date and time
    print(machine.RTC().datetime())

    print_times()
