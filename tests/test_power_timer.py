from unittest import TestCase, mock

import machine
from src.power_timer import PowerTimer
from tests.utils import AssertNoFilesCreatedMixin, MockOpen


class PowerTimerTestCase(AssertNoFilesCreatedMixin, TestCase):
    def setUp(self):
        super().setUp()
        machine.RTC().datetime((2019, 5, 1, 4, 13, 12, 11, 0))
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

    def test_schedule_next_switch_without_timers(self):

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
        self.assertEqual(
            self.power_timer.info_text(),
            'No switch scheduled. (Last update: 2019-05-01 13:12:11+00:00)'
        )

    def test_schedule_next_switch_in_3min(self):
        mock_open = MockOpen(open_data={
            'timer_days.txt': ('r', '0,1,2,3,4,5,6'),
            'timers.txt': ('r', '13:15 - 14:00')
        })
        with mock.patch('builtins.open', mock_open) as m:
            self.power_timer.schedule_next_switch()
            print(str(self.power_timer))

        self.assertEqual(m._calls, [('timer_days.txt', 'r'), ('timers.txt', 'r')])

        self.assertEqual(
            str(self.power_timer),
            "last_update='2019-05-01 13:12:11+00:00',"
            " next_time=(13, 15),"
            " next_time_ms=180000,"  # 13:12 -> 13:15 -> 3min * 60sec * 1000ms
            " turn_on=True,"
            " active=True,"
            " today_active=True"
        )
        self.assertEqual(
            self.power_timer.info_text(),
            'Switch on in 3 min. at 13:15 h. (Last update: 2019-05-01 13:12:11+00:00)'
        )

    def test_schedule_next_switch_in_90min(self):
        mock_open = MockOpen(open_data={
            'timer_days.txt': ('r', '0,1,2,3,4,5,6'),
            'timers.txt': ('r', '14:42 - 14:00')
        })
        with mock.patch('builtins.open', mock_open) as m:
            self.power_timer.schedule_next_switch()
            print(str(self.power_timer))

        self.assertEqual(m._calls, [('timer_days.txt', 'r'), ('timers.txt', 'r')])

        self.assertEqual(
            str(self.power_timer),
            "last_update='2019-05-01 13:12:11+00:00',"
            " next_time=(14, 42),"
            " next_time_ms=5400000,"  # 13:12 -> 14:42 -> 90min * 60sec * 1000ms
            " turn_on=True,"
            " active=True,"
            " today_active=True"
        )
        self.assertEqual(
            self.power_timer.info_text(),
            'Switch on in 90 min. at 14:42 h. (Last update: 2019-05-01 13:12:11+00:00)'
        )

    def test_schedule_next_switch_today_not_active(self):
        mock_open = MockOpen(open_data={
            'timer_days.txt': ('r', '0,1,2,3,4,6'),  # <- day 5 is missing
            'timers.txt': ('r', '13:13 - 14:00')
        })
        with mock.patch('builtins.open', mock_open) as m:
            self.power_timer.schedule_next_switch()
            print(str(self.power_timer))

        self.assertEqual(m._calls, [('timer_days.txt', 'r'), ('timers.txt', 'r')])

        self.assertEqual(
            str(self.power_timer),
            "last_update='2019-05-01 13:12:11+00:00',"
            " next_time=(13, 13),"
            " next_time_ms=60000,"  # 13:12 -> 13:13 -> 1min * 60sec * 1000ms
            " turn_on=True,"
            " active=True,"
            " today_active=False"
        )
        self.assertEqual(
            self.power_timer.info_text(),
            'Power timer is not active today.'
        )
