

import constants
import machine
import utime
from context import Context
from mpy_tests.test_times_utils import assert_current_timer, save_active_days, save_timers
from pins import Pins
from power_timer import active_today, get_info_text, update_power_timer
from rtc import update_rtc_dict
from tests.base import MicropythonBaseTestCase
from tests.utils.mock_py_config import mock_py_config_context
from times_utils import (get_active_days, get_current_timer, iter_times, pformat_timers,
                         restore_timers)
from timezone import localtime_isoformat


class PowerTimerTestCase(MicropythonBaseTestCase):
    def setUp(self):
        super().setUp()
        machine.RTC().datetime((2019, 5, 1, 4, 13, 12, 11, 0))
        self.context = Context()
        self.context.power_timer_timers = None

    def test_update_relay_switch_without_timers(self):
        with mock_py_config_context():
            assert restore_timers() == ()

            update_power_timer(self.context)

            print(get_info_text(self.context))
            self.assertEqual(get_current_timer(self.context), (None, None, None))

    def test_update_relay_switch_in_1min(self):
        machine.RTC().deinit()  # start time from 1.1.2000 00:00
        with mock_py_config_context():
            save_timers((
                ((0, 1), (1, 0)),
            ))
            save_active_days((0, 1, 2, 3, 4, 5, 6))

            assert machine.RTC().datetime((2000, 1, 1, 6, 0, 0, 0, 0))
            assert localtime_isoformat(sep=' ') == '2000-01-01 00:00:00'

            update_power_timer(self.context)
            print(get_info_text(self.context))

            self.assertEqual(
                get_info_text(self.context),
                'Switch on in 1 min at 00:01 h.'
            )

            self.assertEqual(get_info_text(self.context), 'Switch on in 1 min at 00:01 h.')

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

            assert get_active_days() == (0, 1, 2, 3, 4, 5, 6)

            rtc.datetime((2000, 1, 2, 6, 0, 0, 0, 0))  # set RTC time: 2.1.2000 00:00:00
            assert localtime_isoformat(sep=' ') == '2000-01-02 00:00:00'

            assert_current_timer(  # Turn ON at 10:00
                '72000 -4 h 20:00 2000-01-01T20:00:00'
                ' -> 122400 10 h 10:00 2000-01-02T10:00:00 -> ON',
                self.context
            )

            # init relay in state 'OFF'
            Pins.relay.off()
            assert Pins.relay.state == 'OFF'

            # No manual overwrite and ON timer not yet reached -> OFF and turn ON at 10:00
            update_power_timer(self.context)
            assert active_today() is True
            assert self.context.power_timer_today_active is True
            assert Pins.relay.state == 'OFF'
            self.assertEqual(
                get_info_text(self.context),
                'Switch on in 10 h at 10:00 h.'
            )

            # 2000-01-01 09:59:59 - timer not yet reached
            rtc.datetime((2000, 1, 2, 6, 9, 59, 59, 0))
            update_power_timer(self.context)
            assert Pins.relay.state == 'OFF'
            self.assertEqual(
                get_info_text(self.context),
                'Switch on in 1 sec at 10:00 h.'
            )

            # 2000-01-01 10:00:00 - turn ON by timer
            rtc.datetime((2000, 1, 2, 6, 10, 0, 0, 0))
            update_power_timer(self.context)
            assert Pins.relay.state == 'ON'
            self.assertEqual(
                get_info_text(self.context),
                'Switch off in 10 h at 20:00 h.'
            )

            # 2000-01-01 20:00:00 - turn OFF by timer
            rtc.datetime((2000, 1, 2, 6, 20, 0, 0, 0))
            update_power_timer(self.context)
            assert Pins.relay.state == 'OFF'
            self.assertEqual(
                get_info_text(self.context),
                'Switch on in 14 h at 10:00 h.'
            )

            # 2000-01-02 09:00:00 - manual overwrite
            rtc.datetime((2000, 1, 2, 6, 9, 0, 0, 0))
            update_rtc_dict({
                constants.RTC_KEY_MANUAL_OVERWRITE: utime.time(),
                constants.RTC_KEY_MANUAL_OVERWRITE_TYPE: True  # -> turn ON
            })
            update_power_timer(self.context)
            assert Pins.relay.state == 'ON'
            self.assertEqual(
                get_info_text(self.context),
                'Switch on in 60 min at 10:00 h.'
            )
            # 2000-01-02 09:59:59 - manual overwrite is still active
            rtc.datetime((2000, 1, 2, 6, 9, 59, 59, 0))
            update_power_timer(self.context)
            assert Pins.relay.state == 'ON'
            self.assertEqual(
                get_info_text(self.context),
                'Switch on in 1 sec at 10:00 h.'
            )
            # 2000-01-02 12:00:00 - Normal timer mode, still ON
            rtc.datetime((2000, 1, 2, 6, 12, 0, 0, 0))
            update_power_timer(self.context)
            assert Pins.relay.state == 'ON'
            self.assertEqual(
                get_info_text(self.context),
                'Switch off in 8 h at 20:00 h.'
            )
            # manual overwrite
            update_rtc_dict({
                constants.RTC_KEY_MANUAL_OVERWRITE: utime.time(),
                constants.RTC_KEY_MANUAL_OVERWRITE_TYPE: False  # -> turn OFF
            })
            update_power_timer(self.context)
            assert Pins.relay.state == 'OFF'
            self.assertEqual(
                get_info_text(self.context),
                'Switch off in 8 h at 20:00 h.'
            )
            # 2000-01-02 20:00:00 - Normal timer mode -> switch OFF
            rtc.datetime((2000, 1, 2, 6, 20, 0, 0, 0))
            update_power_timer(self.context)
            assert Pins.relay.state == 'OFF'
            self.assertEqual(
                get_info_text(self.context),
                'Switch on in 14 h at 10:00 h.'
            )
            # manual overwrite
            update_rtc_dict({
                constants.RTC_KEY_MANUAL_OVERWRITE: utime.time(),
                constants.RTC_KEY_MANUAL_OVERWRITE_TYPE: True  # -> turn ON
            })
            update_power_timer(self.context)
            assert Pins.relay.state == 'ON'
            self.assertEqual(
                get_info_text(self.context),
                'Switch on in 14 h at 10:00 h.'
            )
            # 2000-01-01 09:59:59 - timer not yet reached
            rtc.datetime((2000, 1, 2, 6, 9, 59, 59, 0))
            update_power_timer(self.context)
            assert Pins.relay.state == 'ON'
            self.assertEqual(
                get_info_text(self.context),
                'Switch on in 1 sec at 10:00 h.'
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

            update_power_timer(self.context)
            print(get_info_text(self.context))

            assert active_today() is False
            assert self.context.power_timer_today_active is False

            self.assertEqual(
                get_info_text(self.context),
                'Power timer is not active today.'
            )
