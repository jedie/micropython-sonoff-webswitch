import tempfile
from unittest import TestCase, mock


from src.timezone import restore_timezone, save_timezone


class TimezoneTestCase(TestCase):
    def test_restore_without_existing_file(self):
        assert restore_timezone() == 0

    def test_save_restore_times(self):
        with tempfile.NamedTemporaryFile() as f:
            with mock.patch('src.timezone._TIMEZONE_FILENAME', f.name):
                save_timezone(-1)
                assert restore_timezone() == -1

                # Don't save if the same value already exists:

                m = mock.mock_open(read_data='-3')
                with mock.patch('builtins.open', m):
                    save_timezone(-3)
                m.assert_called_once_with(f.name, 'r')

