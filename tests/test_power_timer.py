from unittest import TestCase

from src.power_timer import PowerTimer
from tests.utils import AssertNoFilesCreatedMixin


class PowerTimerTestCase(AssertNoFilesCreatedMixin, TestCase):
    def setUp(self):
        super().setUp()
        self.power_timer = PowerTimer()

    def test_str(self):
        self.assertEqual(
            str(self.power_timer),
            'last_update=None,'
            ' next_time=None,'
            ' next_time_ms=None,'
            ' turn_on=None,'
            ' active=None,'
            ' today_active=None'
        )

    def test_schedule_next_switch(self):
        self.power_timer.schedule_next_switch()
        print(str(self.power_timer))
        self.assertEqual(
            str(self.power_timer),
            "last_update='2019-05-01 13:12:11+00:00',"
            " next_time=None,"
            " next_time_ms=None,"
            " turn_on=None,"
            " active=True,"
            " today_active=True"
        )
