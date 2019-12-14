

import machine
from power_timer_schedule import active_today
from src.power_timer import PowerTimer
from tests.base import MicropythonBaseTestCase
from tests.utils.mock_py_config import mock_py_config_context
from times_utils import save_active_days, save_timers
from timezone import localtime_isoformat


class PowerTimerTestCase(MicropythonBaseTestCase):
    def setUp(self):
        super().setUp()
        machine.RTC().datetime((2019, 5, 1, 4, 13, 12, 11, 0))

    def test_str(self):
        self.assertEqual(
            str(PowerTimer()),
            'last_update=None,'
            ' next_timer_epoch=None,'
            ' turn_on=None,'
            ' active=None,'
            ' today_active=None'
        )

    def test_schedule_next_switch_without_timers(self):
        power_timer = PowerTimer()
        power_timer.schedule_next_switch()
        print(str(power_timer))
        self.assertEqual(
            str(power_timer),
            "last_update='2019-05-01 13:12:11',"
            " next_timer_epoch=None,"
            " turn_on=None,"
            " active=True,"
            " today_active=True"
        )
        self.assertEqual(
            power_timer.info_text(),
            'No switch scheduled. (Last update: 2019-05-01 13:12:11)'
        )

    def test_schedule_next_switch_in_1min(self):
        machine.RTC().deinit()  # start time from 1.1.2000 00:00
        with mock_py_config_context():
            save_timers((
                ((0, 1), (1, 0)),
            ))
            save_active_days((0, 1, 2, 3, 4, 5, 6))

            assert machine.RTC().datetime() == (2000, 1, 1, 5, 0, 0, 0, 0)
            assert localtime_isoformat(sep=' ') == '2000-01-01 00:00:00'

            power_timer = PowerTimer()
            power_timer.schedule_next_switch()
            print(str(power_timer))

            self.assertEqual(
                power_timer.info_text(),
                'Switch on in 1 min at 00:01 h. (Last update: 2000-01-01 00:00:00)'
            )

            self.assertEqual(
                str(power_timer),
                "last_update='2000-01-01 00:00:00',"
                " next_timer_epoch=60,"
                " turn_on=True,"
                " active=True,"
                " today_active=True"
            )

    def test_schedule_next_switch_in_1h(self):
        machine.RTC().deinit()  # start time from 1.1.2000 00:00
        with mock_py_config_context():
            save_timers((
                ((1, 0), (2, 0)),
            ))
            save_active_days((0, 1, 2, 3, 4, 5, 6))

            assert machine.RTC().datetime() == (2000, 1, 1, 5, 0, 0, 0, 0)
            assert localtime_isoformat(sep=' ') == '2000-01-01 00:00:00'

            power_timer = PowerTimer()
            power_timer.schedule_next_switch()
            print(str(power_timer))

            self.assertEqual(
                power_timer.info_text(),
                'Switch on in 60 min at 01:00 h. (Last update: 2000-01-01 00:00:00)'
            )

            self.assertEqual(
                str(power_timer),
                "last_update='2000-01-01 00:00:00',"
                " next_timer_epoch=3600,"
                " turn_on=True,"
                " active=True,"
                " today_active=True"
            )

    def test_schedule_next_switch_today_not_active(self):
        machine.RTC().deinit()  # start time from 1.1.2000 00:00
        with mock_py_config_context():
            save_timers((
                ((1, 0), (2, 0)),
            ))
            save_active_days((0, 1, 2, 3, 4, 6))  # <- day 5 is missing

            assert machine.RTC().datetime() == (2000, 1, 1, 5, 0, 0, 0, 0)
            assert localtime_isoformat(sep=' ') == '2000-01-01 00:00:00'

            assert active_today() is False

            power_timer = PowerTimer()
            power_timer.schedule_next_switch()
            print(str(power_timer))

            self.assertEqual(
                power_timer.info_text(),
                'Power timer is not active today. (Last update: 2000-01-01 00:00:00)'
            )

            self.assertEqual(
                str(power_timer),
                "last_update='2000-01-01 00:00:00',"
                " next_timer_epoch=None,"
                " turn_on=None,"
                " active=True,"
                " today_active=False"
            )
