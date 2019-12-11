from unittest import TestCase

from mpy_tests.test_power_timer import test_power_timer
from mpy_tests.test_timezone import test_time_basics, test_timezone_shift


class MPyTestCase(TestCase):
    def test_call_test_time_basics(self):
        test_time_basics()

    def test_call_timezone_shift_tests(self):
        test_timezone_shift()

    def test_call_test_power_timer(self):
        test_power_timer()
