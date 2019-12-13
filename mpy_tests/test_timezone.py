import machine
import utime
from timezone import get_local_epoch, localtime_isoformat, restore_timezone, save_timezone


def test_time_basics():
    rtc = machine.RTC()
    print('rtc.datetime():', rtc.datetime())  # ...........(2000, 1, 1, 5, 0, 0, 0, 0)

    rtc.datetime((2019, 5, 1, 4, 13, 12, 11, 0))  # same as in tests.mocks.machine.RTC.datetime

    print('rtc.datetime():', rtc.datetime())  # ...........(2019, 5, 1, 2, 13, 12, 11, 0)
    print('utime.localtime():', utime.localtime())  # .....(2019, 5, 1, 13, 12, 11, 2, 121)

    result = utime.localtime(0)
    print('utime.localtime(0):', result)
    assert result == (2000, 1, 1, 0, 0, 0, 5, 1), result

    result = utime.mktime((2000, 1, 1, 0, 0, 0, 5, 1))
    print('utime.mktime((2000, 1, 1, 0, 0, 0, 5, 1)):', result)
    assert result == 0, result

    result = utime.mktime((2019, 1, 1, 0, 0, 0, 5, 1))
    print('utime.mktime((2019, 1, 1, 0, 0, 0, 5, 1)):', result)
    assert result == 599616000, result


def test_localtime_isoformat():
    assert localtime_isoformat(epoch=0, add_offset=True) == '2000-01-01T00:00:00-01:00'
    assert localtime_isoformat(epoch=59) == '2000-01-01T00:00:59'
    assert localtime_isoformat(epoch=1 * 60) == '2000-01-01T00:01:00'
    assert localtime_isoformat(epoch=2 * 60 * 60) == '2000-01-01T02:00:00'
    assert localtime_isoformat(epoch=2 * 24 * 60 * 60) == '2000-01-03T00:00:00'
    assert localtime_isoformat(epoch=1 * 30 * 24 * 60 * 60) == '2000-01-31T00:00:00'
    assert localtime_isoformat(epoch=1 * 31 * 24 * 60 * 60) == '2000-02-01T00:00:00'


def test_get_local_epoch():
    assert get_local_epoch() > utime.mktime((2019, 12, 13, 0, 0, 0, 5, 1))


def run_all_timezone_tests():
    test_time_basics()

    save_timezone(offset_h=-1)
    assert restore_timezone() == -1

    test_localtime_isoformat()


if __name__ == '__main__':
    print('Test timezone...')
    origin_offset_h = restore_timezone()
    try:
        run_all_timezone_tests()
    finally:
        save_timezone(offset_h=origin_offset_h)
    print('OK')
