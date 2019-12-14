from pathlib import Path
from unittest import TestCase

import machine


def get_all_config_files(path='.'):
    path = Path(path)
    config_files = list(path.glob('config_*.py'))
    config_files += list(path.glob('config_*.json'))
    return config_files


class MicropythonBaseTestCase(TestCase):
    @classmethod
    def setUpClass(cls):
        config_files = get_all_config_files()
        assert not config_files, f'Config files exists before test start: %s' % config_files
        super().setUpClass()

    def setUp(self):
        super().setUp()
        machine.RTC().datetime((2019, 5, 1, 4, 13, 12, 11, 0))

    def tearDown(self):
        config_files = get_all_config_files()
        assert not config_files, f'Mock error: Config files created: %s' % config_files

        super().tearDown()
