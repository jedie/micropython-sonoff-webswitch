import gc
import sys

import machine
import utime
from micropython import const
from timezone import localtime_isoformat, restore_timezone

_h2sec = const(60 * 60)  # multiplier for calc hours into seconds


def rtc2local_time():
    rtc = machine.RTC()

    # year, month, mday, hour, minute, second, weekday, yearday
    utc_time_tuple = utime.localtime()

    # year, month, day, weekday, hours, minutes, seconds, ???
    utc_rtc_tuple = rtc.datetime()
    print('set from..:', utc_rtc_tuple)

    local_time_tuple = utime.localtime(
        utime.mktime(utc_time_tuple) + (
            restore_timezone() * _h2sec * -1
        )
    )

    # Shift RTC time from UTC to local time:
    local_rtc_tuple = utc_rtc_tuple[:4] + local_time_tuple[3:5] + utc_rtc_tuple[6:]
    print('set to....:', local_rtc_tuple)
    rtc.datetime(local_rtc_tuple)  # set RTC time


def ntp_sync():
    import ntptime

    if utime.localtime()[0] < 2019:
        # time was never synced: assume it's default start time in UTC
        offset_h = 0  # don't add local saved time zone offset
    else:
        offset_h = None  # load offset via restore_timezone()

    print('Synchronize time from %r ...' % ntptime.host)
    print('old UTC.....:', localtime_isoformat(offset_h=offset_h, add_offset=True))
    for s in range(5):
        try:
            ntptime.settime()
        except Exception as e:
            print('Error syncing time: %s, retry in %s sec.' % (e, s * 5))
            utime.sleep(s * 5)
        else:
            del ntptime
            del sys.modules['ntptime']
            gc.collect()

            print('new UTC.....:', localtime_isoformat(offset_h=offset_h, add_offset=True))
            rtc2local_time()
            print('new local...:', localtime_isoformat(offset_h=offset_h, add_offset=True))

            return True

    from reset import ResetDevice
    ResetDevice(reason='Failed NTP sync').reset()


if __name__ == '__main__':

    def print_times():
        # year, month, day, weekday, hours, minutes, seconds, ???
        print('machine.RTC().datetime():', machine.RTC().datetime())

        # http://docs.micropython.org/en/latest/library/uutime.html#uutime.localtime
        # year, month, mday, hour, minute, second, weekday, yearday
        print('utime.localtime().......:', utime.localtime())

    print_times()
    ntp_sync()
    print_times()
