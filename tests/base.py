import os
from pathlib import Path
from unittest import TestCase

import asynctest
import machine
from context import Context
from uasyncio import StreamReader, StreamWriter
from watchdog import Watchdog
from webswitch import WebServer

WIFI_EXAMPLE = '_config_wifi-example.json'
BASE_PATH = Path(__file__).parent.parent  # .../micropython-sonoff-webswitch/
SRC_PATH = Path(BASE_PATH, 'src')  # .../micropython-sonoff-webswitch/src/


class ChangeWorkDirContext:
    def __init__(self):
        self.old_cwd = Path.cwd()

    def __enter__(self):
        assert SRC_PATH.is_dir()
        os.chdir(SRC_PATH)

    def __exit__(self, exc_type, exc_val, exc_tb):
        os.chdir(self.old_cwd)


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
        self.context = Context
        self.context.power_timer_timers = None

    def tearDown(self):
        config_files = get_all_config_files()
        assert not config_files, f'Mock error: Config files created: %s' % config_files
        super().tearDown()


class WebServerTestCase(asynctest.TestCase, MicropythonBaseTestCase):
    async def get_request(self, request_line):
        with ChangeWorkDirContext():
            context = Context  # no instance!

            context.watchdog = Watchdog(context)

            web_server = WebServer(context=context, version='v0.1')

            reader = asynctest.mock.Mock(StreamReader)
            writer = StreamWriter()

            reader.readline.return_value = request_line

            await web_server.request_handler(reader, writer)

            return writer.get_response(), web_server.message
