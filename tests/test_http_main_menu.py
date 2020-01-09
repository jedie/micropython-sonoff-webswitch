import utime
from tests.base import WebServerTestCase


class HttpMainMenuTestCase(WebServerTestCase):

    async def test_non_well_form_request(self):
        response = await self.get_request(
            request_line=b"GET-totaly-bullshit-HTTP/1.1"
        )
        assert response == b'HTTP/1.0 303 Moved\r\nLocation: /main/menu/\r\n\r\n'
        assert self.web_server.message == 'not enough values to unpack (expected 3, got 1)'

    async def test_get_main_menu(self):
        assert utime.localtime() == (2019, 5, 1, 13, 12, 11, 2, 121)
        response = await self.get_request(request_line=b"GET /main/menu/ HTTP/1.1")
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
        assert self.web_server.message == 'Web server started...'
