from pathlib import Path
from unittest import mock

from times_utils import _ACTIVE_DAYS_FILENAME, _TIMERS_FILENAME


class AssertNoFilesCreatedMixin:
    def tearDown(self):
        for filename in (_TIMERS_FILENAME, _ACTIVE_DAYS_FILENAME):
            assert not Path(filename).exists(), f'ERROR: File {filename!r} exists!'


class MockOpen:

    def __init__(self, open_data):
        self._calls = []
        self.open_data = open_data

    def __call__(self, filename, mode):
        print(f'mocked open {filename!r}')
        self._calls.append((filename, mode))

        try:
            should_mode, content = self.open_data[filename]
        except KeyError:
            raise FileNotFoundError(filename)

        if mode != should_mode:
            raise AssertionError(
                f'Wrong file mode used: should: {should_mode!r} is: {mode!r}'
            )

        file_object = mock.mock_open(read_data=content).return_value
        file_object.__iter__.return_value = content.splitlines(True)
        return file_object
