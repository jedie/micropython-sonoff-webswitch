from unittest import TestCase

from tests.mocks import utime


class MicroPythonMocksTestCase(TestCase):
    def test_utime(self):
        assert utime.localtime(0) == (2000, 1, 1, 0, 0, 0, 5, 1)
        assert utime.mktime(utime.localtime(0)) == 0
