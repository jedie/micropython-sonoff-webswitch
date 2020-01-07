import os
from pathlib import Path

import asynctest
from context import Context
from uasyncio import StreamReader, StreamWriter
from watchdog import Watchdog
from webswitch import WebServer

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


class TestMockASocket(asynctest.TestCase):
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

    def assert_response(self, response, expected_response):
        if response == expected_response:
            return
        print('-' * 100)
        print(response)
        print('-' * 100)
        assert expected_response == response

    def assert_response_parts(self, response, parts):
        for part in parts:
            if part not in response:
                print('-' * 100)
                print(response)
                print('-' * 100)
                assert part in response

    async def test_non_well_form_request(self):
        response, server_message = await self.get_request(
            request_line=b"GET-totaly-bullshit-HTTP/1.1"
        )
        assert response == 'HTTP/1.0 303 Moved\r\nLocation: /main/menu/\r\n\r\n'
        assert server_message == 'not enough values to unpack (expected 3, got 1)'

    async def test_get_main_menu(self):
        response, server_message = await self.get_request(request_line=b"GET /main/menu/ HTTP/1.1")
        self.assert_response_parts(
            response,
            parts=(
                'HTTP/1.0 200 OK',
                '<html>',
                '<title>network name-04030201 - OFF</title>',
                '<p>Power switch state: <strong>OFF</strong></p>',
                '<p>Web server started...</p>',
                'RAM total: 1.95 KB, used: 0.98 KB, free: 0.98 KB<br>',
                'Server local time: 2000-01-01 00:00:00',
                '</html>'
            )
        )
        assert 'Web server started...' == server_message
