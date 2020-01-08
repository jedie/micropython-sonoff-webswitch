

import machine
import utime
from tests.base import MicropythonBaseTestCase


class MicroPythonMocksTestCase(MicropythonBaseTestCase):
    def test_utime(self):
        assert utime.localtime(0) == (2000, 1, 1, 0, 0, 0, 5, 1)
        assert utime.mktime(utime.localtime(0)) == 0

        rtc = machine.RTC()
        rtc.datetime((2019, 12, 27, 4, 11, 49, 35, 0))
        assert utime.localtime() == (2019, 12, 27, 11, 49, 35, 4, 361)
