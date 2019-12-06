import tempfile
from unittest import TestCase, mock

from times_utils import (get_ms_until_next_timer, get_next_timer, parse_timers, pformat_timers,
                         restore_timers, save_timers, validate_times)


class ParseTimesTestCase(TestCase):

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
        self.assertRaises(ValueError)
        assert tuple(parse_timers('''
            1:23 4:56
            Foo 19:00 X 20:00 Bar
        ''')) == (
            ((1, 23), (4, 56)),
            ((19, 0), (20, 0))
        )

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
        assert tuple(restore_timers()) == ()

    def test_save_restore_times(self):
        with tempfile.NamedTemporaryFile() as f:
            with mock.patch('times_utils._TIMERS_FILENAME', f.name):
                save_timers([
                    ((1, 23), (4, 56)),
                    ((19, 0), (20, 0))
                ])
                assert tuple(restore_timers()) == (
                    ((1, 23), (4, 56)),
                    ((19, 0), (20, 0))
                )

                # Don't save if the same timers already exists:

                m = mock.mock_open(read_data='''
                    1:23 - 4:56
                    19:00 - 20:00
                ''')
                with mock.patch('times_utils.open', m):
                    save_timers((
                        ((1, 23), (4, 56)),
                        ((19, 0), (20, 0))
                    ))
                m.assert_called_once_with(f.name, 'r')

    def test_get_next_timer(self):
        m = mock.mock_open(read_data='''
            1:23 - 4:56
            19:00 - 20:00
        ''')
        with mock.patch('times_utils.open', m):
            assert get_next_timer(current_time=(1, 22)) == (True, (1, 23))
            assert get_next_timer(current_time=(1, 23)) == (False, (4, 56))
            assert get_next_timer(current_time=(4, 55)) == (False, (4, 56))
            assert get_next_timer(current_time=(4, 56)) == (True, (19, 00))
            assert get_next_timer(current_time=(19, 00)) == (False, (20, 00))
            assert get_next_timer(current_time=(20, 00)) == (True, (1, 23))
            assert get_next_timer(current_time=(23, 59)) == (True, (1, 23))
            assert get_next_timer(current_time=(0, 0)) == (True, (1, 23))
            assert get_next_timer(current_time=(0, 1)) == (True, (1, 23))

    def test_get_next_timer_always_on(self):
        m = mock.mock_open(read_data='''
            0:00 - 23:59
        ''')
        with mock.patch('times_utils.open', m):
            assert get_next_timer(current_time=(0, 0)) == (False, (23, 59))
            assert get_next_timer(current_time=(0, 1)) == (False, (23, 59))
            assert get_next_timer(current_time=(23, 58)) == (False, (23, 59))
            assert get_next_timer(current_time=(23, 59)) == (True, (0, 0))

    def test_get_next_timer_empty(self):
        m = mock.mock_open(read_data='')
        with mock.patch('times_utils.open', m):
            assert get_next_timer(current_time=(0, 0)) == (None, None)

    def test_get_ms_until_next_timer(self):
        m = mock.mock_open(read_data='10:01 - 11:35')
        with mock.patch('times_utils.open', m):
            assert get_ms_until_next_timer(current_time=(10, 0)) == (True, (10, 1), 1000)
            assert get_ms_until_next_timer(current_time=(10, 35)) == (False, (11, 35), 60000)

    def test_get_ms_until_next_timer_empty(self):
        m = mock.mock_open(read_data='')
        with mock.patch('times_utils.open', m):
            assert get_ms_until_next_timer(current_time=(12, 34)) == (None, None, None)
