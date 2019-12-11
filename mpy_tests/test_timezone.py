import machine
import utime
from timezone import clock_time_shift, datetime_shift


def test_time_basics():
    rtc = machine.RTC()
    print('rtc.datetime():', rtc.datetime())  # ...........(2000, 1, 1, 5, 0, 0, 0, 0)

    rtc.datetime((2019, 5, 1, 4, 13, 12, 11, 0))  # same as in tests.mocks.machine.RTC.datetime

    print('rtc.datetime():', rtc.datetime())  # ...........(2019, 5, 1, 2, 13, 12, 11, 0)
    print('utime.localtime():', utime.localtime())  # .....(2019, 5, 1, 13, 12, 11, 2, 121)

    result = utime.localtime(0)
    print('utime.localtime(0):', result)
    assert result == (2000, 1, 1, 0, 0, 0, 5, 1)

    result = utime.mktime((2000, 1, 1, 0, 0, 0, 5, 1))
    print('utime.mktime((2000, 1, 1, 0, 0, 0, 5, 1)):', result)
    assert result == 0


def test_timezone_shift():
    test_data = (
        ((2019, 5, 1, 4, 13, 12, 2, 121), +1, (2019, 5, 1, 5, 13, 12, 2, 121)),
        ((2019, 5, 1, 4, 13, 12, 2, 121), -1, (2019, 5, 1, 3, 13, 12, 2, 121)),

        ((2019, 5, 1, 0, 0, 12, 2, 121), +1, (2019, 5, 1, 1, 0, 12, 2, 121)),
        ((2019, 5, 1, 0, 0, 12, 2, 121), -1, (2019, 4, 30, 23, 0, 12, 1, 120)),

        ((2019, 5, 1, 0, 0, 12, 2, 121), +12, (2019, 5, 1, 12, 0, 12, 2, 121)),
        ((2019, 5, 1, 0, 0, 12, 2, 121), -12, (2019, 4, 30, 12, 0, 12, 1, 120)),
    )
    for src, offset_h, should_dst in test_data:
        is_dst = datetime_shift(dt=src, offset_h=offset_h)
        print('datetime_shift(%r, %+i) -> %r' % (
            src, offset_h, is_dst
        ))
        assert is_dst == should_dst, '%r != %r' % (is_dst, should_dst)

    test_data = (
        ((20, 30), +1, (21, 30)),
        ((20, 30), -1, (19, 30)),

        ((0, 12), +1, (1, 12)),
        ((0, 12), -1, (23, 12)),

        ((0, 1), +12, (12, 1)),
        ((0, 1), -12, (12, 1)),
    )
    for src, offset_h, should_dst in test_data:
        is_dst = clock_time_shift(clock_time=src, offset_h=offset_h)
        print('clock_time_shift(%02i:%02i, %+i) -> %02i:%02i' % (
            src[0], src[1], offset_h, is_dst[0], is_dst[1]
        ))
        assert is_dst == should_dst, '%r != %r' % (is_dst, should_dst)


if __name__ == '__main__':
    test_time_basics()
    test_timezone_shift()
    print('OK')
