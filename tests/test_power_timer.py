

import constants
import machine
import utime
from mpy_tests.test_times_utils import assert_current_timer
from pins import Pins
from power_timer_schedule import active_today
from rtc import update_rtc_dict
from src.power_timer import PowerTimer
from tests.base import MicropythonBaseTestCase
from tests.utils.mock_py_config import mock_py_config_context
from times_utils import iter_times, pformat_timers, restore_timers, save_active_days, save_timers
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

    def test_update_relay_switch_without_timers(self):
        power_timer = PowerTimer()
        power_timer.update_relay_switch()
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

    def test_update_relay_switch_in_1min(self):
        machine.RTC().deinit()  # start time from 1.1.2000 00:00
        with mock_py_config_context():
            save_timers((
                ((0, 1), (1, 0)),
            ))
            save_active_days((0, 1, 2, 3, 4, 5, 6))

            assert machine.RTC().datetime((2000, 1, 1, 6, 0, 0, 0, 0))
            assert localtime_isoformat(sep=' ') == '2000-01-01 00:00:00'

            power_timer = PowerTimer()
            power_timer.update_relay_switch()
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

    def test_relay_switch_timers_and_overwrite(self):
        rtc = machine.RTC()
        with mock_py_config_context():
            save_timers((
                ((10, 0), (20, 0)),
            ))
            timers = restore_timers()
            assert pformat_timers(timers) == '10:00 - 20:00'
            assert list(iter_times(timers)) == [(True, (10, 0, 0)), (False, (20, 0, 0))]

            save_active_days((0, 1, 2, 3, 4, 5, 6))

            rtc.datetime((2000, 1, 2, 6, 0, 0, 0, 0))  # set RTC time: 2.1.2000 00:00:00
            assert localtime_isoformat(sep=' ') == '2000-01-02 00:00:00'

            assert_current_timer(  # Turn ON at 10:00
                '72000 -4 h 20:00 2000-01-01T20:00:00'
                ' -> 122400 10 h 10:00 2000-01-02T10:00:00 -> ON'
            )

            power_timer = PowerTimer()

            # init relay in state 'OFF'
            Pins.relay.off()
            assert Pins.relay.state == 'OFF'

            # No manual overwrite and ON timer not yet reached -> OFF and turn ON at 10:00
            power_timer.update_relay_switch()
            assert Pins.relay.state == 'OFF'
            self.assertEqual(
                power_timer.info_text(),
                'Switch on in 10 h at 10:00 h. (Last update: 2000-01-02 00:00:00)'
            )

            # 2000-01-01 09:59:59 - timer not yet reached
            rtc.datetime((2000, 1, 2, 6, 9, 59, 59, 0))
            power_timer.update_relay_switch()
            assert Pins.relay.state == 'OFF'
            self.assertEqual(
                power_timer.info_text(),
                'Switch on in 1 sec at 10:00 h. (Last update: 2000-01-02 09:59:59)'
            )

            # 2000-01-01 10:00:00 - turn ON by timer
            rtc.datetime((2000, 1, 2, 6, 10, 0, 0, 0))
            power_timer.update_relay_switch()
            assert Pins.relay.state == 'ON'
            self.assertEqual(
                power_timer.info_text(),
                'Switch off in 10 h at 20:00 h. (Last update: 2000-01-02 10:00:00)'
            )

            # 2000-01-01 20:00:00 - turn OFF by timer
            rtc.datetime((2000, 1, 2, 6, 20, 0, 0, 0))
            power_timer.update_relay_switch()
            assert Pins.relay.state == 'OFF'
            self.assertEqual(
                power_timer.info_text(),
                'Switch on in 14 h at 10:00 h. (Last update: 2000-01-02 20:00:00)'
            )

            # 2000-01-02 09:00:00 - manual overwrite
            rtc.datetime((2000, 1, 2, 6, 9, 0, 0, 0))
            update_rtc_dict({
                constants.RTC_KEY_MANUAL_OVERWRITE: utime.time(),
                constants.RTC_KEY_MANUAL_OVERWRITE_TYPE: True  # -> turn ON
            })
            power_timer.update_relay_switch()
            assert Pins.relay.state == 'ON'
            self.assertEqual(
                power_timer.info_text(),
                'Switch on in 60 min at 10:00 h. (Last update: 2000-01-02 09:00:00)'
            )
            # 2000-01-02 09:59:59 - manual overwrite is still active
            rtc.datetime((2000, 1, 2, 6, 9, 59, 59, 0))
            power_timer.update_relay_switch()
            assert Pins.relay.state == 'ON'
            self.assertEqual(
                power_timer.info_text(),
                'Switch on in 1 sec at 10:00 h. (Last update: 2000-01-02 09:59:59)'
            )
            # 2000-01-02 12:00:00 - Normal timer mode, still ON
            rtc.datetime((2000, 1, 2, 6, 12, 0, 0, 0))
            power_timer.update_relay_switch()
            assert Pins.relay.state == 'ON'
            self.assertEqual(
                power_timer.info_text(),
                'Switch off in 8 h at 20:00 h. (Last update: 2000-01-02 12:00:00)'
            )
            # manual overwrite
            update_rtc_dict({
                constants.RTC_KEY_MANUAL_OVERWRITE: utime.time(),
                constants.RTC_KEY_MANUAL_OVERWRITE_TYPE: False  # -> turn OFF
            })
            power_timer.update_relay_switch()
            assert Pins.relay.state == 'OFF'
            self.assertEqual(
                power_timer.info_text(),
                'Switch off in 8 h at 20:00 h. (Last update: 2000-01-02 12:00:00)'
            )
            # 2000-01-02 20:00:00 - Normal timer mode -> switch OFF
            rtc.datetime((2000, 1, 2, 6, 20, 0, 0, 0))
            power_timer.update_relay_switch()
            assert Pins.relay.state == 'OFF'
            self.assertEqual(
                power_timer.info_text(),
                'Switch on in 14 h at 10:00 h. (Last update: 2000-01-02 20:00:00)'
            )
            # manual overwrite
            update_rtc_dict({
                constants.RTC_KEY_MANUAL_OVERWRITE: utime.time(),
                constants.RTC_KEY_MANUAL_OVERWRITE_TYPE: True  # -> turn ON
            })
            power_timer.update_relay_switch()
            assert Pins.relay.state == 'ON'
            self.assertEqual(
                power_timer.info_text(),
                'Switch on in 14 h at 10:00 h. (Last update: 2000-01-02 20:00:00)'
            )
            # 2000-01-01 09:59:59 - timer not yet reached
            rtc.datetime((2000, 1, 2, 6, 9, 59, 59, 0))
            power_timer.update_relay_switch()
            assert Pins.relay.state == 'ON'
            self.assertEqual(
                power_timer.info_text(),
                'Switch on in 1 sec at 10:00 h. (Last update: 2000-01-02 09:59:59)'
            )

    def test_update_relay_switch_today_not_active(self):
        machine.RTC().deinit()  # start time from 1.1.2000 00:00
        with mock_py_config_context():
            save_timers((
                ((1, 0), (2, 0)),
            ))
            save_active_days((0, 1, 2, 3, 4, 6))  # <- day 5 is missing

            assert machine.RTC().datetime((2000, 1, 1, 5, 0, 0, 0, 0))
            assert localtime_isoformat(sep=' ') == '2000-01-01 00:00:00'

            assert active_today() is False

            power_timer = PowerTimer()
            power_timer.update_relay_switch()
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
