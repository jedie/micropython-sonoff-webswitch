import tempfile
from unittest import TestCase, mock

from times_utils import parse_timers, pformat_timers, restore_timers, save_timers, validate_times


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
        assert restore_timers() == ()

    def test_save_restore_times(self):
        with tempfile.NamedTemporaryFile() as f:
            with mock.patch('times_utils._TIMERS_FILENAME', f.name):
                save_timers([
                    ((1, 23), (4, 56)),
                    ((19, 0), (20, 0))
                ])
                assert restore_timers() == (
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
