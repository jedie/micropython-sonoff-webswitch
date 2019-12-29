

import machine
from mpy_tests.test_times_utils import save_timers
from power_timer import update_power_timer
from src.times_utils import (get_current_timer, parse_timers, pformat_timers, restore_timers,
                             validate_times)
from tests.base import MicropythonBaseTestCase
from tests.utils.mock_py_config import mock_py_config_context


class ParseTimesTestCase(MicropythonBaseTestCase):

    def test_parse_timers(self):
        assert tuple(parse_timers('''
            1:23 - 4:56
            19:00 - 20:00
        ''')) == (
            ((1, 23), (4, 56)),
            ((19, 0), (20, 0))
        )

    def test_parse_timers_emty_lines(self):
        assert tuple(parse_timers('''
            1:23 - 4:56

            19:00 - 20:00
        ''')) == (
            ((1, 23), (4, 56)),
            ((19, 0), (20, 0))
        )

    def test_parse_timers2(self):
        assert tuple(parse_timers('''
            1:23 4:56
            Foo 19:00 X 20:00 Bar
        ''')) == (
            ((1, 23), (4, 56)),
            ((19, 0), (20, 0))
        )

    def test_parse_timers_not_sequential1(self):
        with self.assertRaises(ValueError) as cm:
            tuple(parse_timers('''
                2:00 - 1:00
            '''))
        self.assertEqual(cm.exception.args[0], 'Times in line 1 are not sequential!')

    def test_parse_timers_not_sequential2(self):
        with self.assertRaises(ValueError) as cm:
            tuple(parse_timers('''
                10:00 - 12:00
                10:30 - 13:00
            '''))
        self.assertEqual(cm.exception.args[0], 'Times in line 2 are not sequential!')

    def test_parse_timers_error1(self):
        with self.assertRaises(ValueError) as cm:
            tuple(parse_timers('''
                1:23 - 4:56
                19:00 - :00
            '''))
        self.assertEqual(cm.exception.args[0], 'Wrong time in line 2')

    def test_parse_timers_error2(self):
        with self.assertRaises(ValueError) as cm:
            tuple(parse_timers('''
                1:23 - :56
                19:00 - 5:00
            '''))
        self.assertEqual(cm.exception.args[0], 'Wrong time in line 1')

    def test_pformat_timers(self):
        assert pformat_timers([
            ((1, 23), (4, 56)),
            ((19, 0), (20, 0))
        ]) == '01:23 - 04:56\n19:00 - 20:00'

    def test_validate_times(self):
        assert validate_times([
            ((1, 23), (4, 56)),
            ((19, 0), (20, 0))
        ]) is True

    def test_validate_times_wrong_order1(self):
        with self.assertRaises(ValueError) as cm:
            validate_times([((19, 1), (19, 0))])
        self.assertEqual(cm.exception.args[0], '19:00 is in wrong order')

    def test_validate_times_wrong_order2(self):
        with self.assertRaises(ValueError) as cm:
            validate_times([
                ((1, 23), (4, 56)),
                ((4, 55), (20, 0))
            ])
        self.assertEqual(cm.exception.args[0], '04:55 is in wrong order')

    def test_validate_times_hour_out_of_range1(self):
        with self.assertRaises(ValueError) as cm:
            validate_times([
                ((1, 23), (4, 56)),
                ((19, 0), (24, 0))
            ])
        self.assertEqual(cm.exception.args[0], '24:00 is not valid')

    def test_validate_times_hour_out_of_range2(self):
        with self.assertRaises(ValueError) as cm:
            validate_times([
                ((1, 23), (-4, 56)),
                ((19, 0), (23, 0))
            ])
        self.assertEqual(cm.exception.args[0], '-4:56 is not valid')

    def test_validate_times_minutes_out_of_range1(self):
        with self.assertRaises(ValueError) as cm:
            validate_times([
                ((1, 23), (4, 60)),
                ((19, 1), (20, 0))
            ])
        self.assertEqual(cm.exception.args[0], '04:60 is not valid')

    def test_validate_times_minutes_out_of_range2(self):
        with self.assertRaises(ValueError) as cm:
            validate_times([
                ((1, 23), (4, 56)),
                ((19, -1), (20, 0))
            ])
        self.assertEqual(cm.exception.args[0], '19:-1 is not valid')

    def test_restore_times_without_existing_file(self):
        with mock_py_config_context():
            assert restore_timers() == ()

    def test_get_current_timer(self):
        with mock_py_config_context():
            save_timers((
                ((0, 0), (0, 1)),
                ((0, 2), (0, 3)),
            ))
            update_power_timer(self.context)

            rtc = machine.RTC()
            rtc.datetime((2000, 1, 1, 5, 0, 0, 0, 0))  # 00:00
            assert get_current_timer(self.context) == (0, False, 60)

            rtc.datetime((2000, 1, 1, 5, 0, 1, 0, 0))  # 00:01
            assert get_current_timer(self.context) == (60, True, 120)

            rtc.datetime((2000, 1, 1, 5, 0, 2, 0, 0))  # 00:02
            assert get_current_timer(self.context) == (120, False, 180)

            rtc.datetime((2000, 1, 1, 5, 0, 3, 0, 0))  # 00:03 -> next timer is on next day!
            assert get_current_timer(self.context) == (180, True, 86400)

    def test_get_current_timer_empty(self):
        with mock_py_config_context():
            self.context.power_timer_timers = []
            assert get_current_timer(self.context) == (None, None, None)
