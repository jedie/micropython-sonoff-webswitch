import utime
from tests.base import WebServerTestCase


class HttpMainMenuTestCase(WebServerTestCase):

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
        assert utime.localtime() == (2019, 5, 1, 13, 12, 11, 2, 121)
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
                'Server local time: 2019-05-01 13:12:11',
                '</html>'
            )
        )
        assert 'Web server started...' == server_message
