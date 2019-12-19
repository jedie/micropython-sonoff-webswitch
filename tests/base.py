from pathlib import Path
from unittest import TestCase

import machine

WIFI_EXAMPLE = '_config_wifi-example.json'


def get_all_config_files(path='.'):
    path = Path(path)
    config_files = [i.name for i in path.glob('_config_*.py')]
    config_files += [i.name for i in path.glob('_config_*.json')]
    if WIFI_EXAMPLE in config_files:
        config_files.remove(WIFI_EXAMPLE)
    return config_files


class MicropythonBaseTestCase(TestCase):
    def setUp(self):
        super().setUp()
        machine.RTC().datetime((2019, 5, 1, 4, 13, 12, 11, 0))
        config_files = get_all_config_files()
        assert not config_files, f'Config files exists before test start: %s' % config_files

    def tearDown(self):
        config_files = get_all_config_files()
        assert not config_files, f'Mock error: Config files created: %s' % config_files
        super().tearDown()
