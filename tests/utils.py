from pathlib import Path

from times_utils import _ACTIVE_DAYS_FILENAME, _TIMERS_FILENAME


class AssertNoFilesCreatedMixin:
    def tearDown(self):
        for filename in (_TIMERS_FILENAME, _ACTIVE_DAYS_FILENAME):
            assert not Path(filename).exists(), f'ERROR: File {filename!r} exists!'
