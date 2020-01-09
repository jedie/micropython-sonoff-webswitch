
from unittest import mock

from tests.base import WebServerTestCase
from timezone import restore_timezone


class HttpMainMenuTestCase(WebServerTestCase):
    async def test_set_timezone(self):

        assert restore_timezone() == 0

        # Set timer:

        with mock.patch('ntptime.settime') as mock_settime:
            response = await self.get_request(
                request_line=(
                    b"GET /settings/submit_timezone/?offset=-1 HTTP/1.1"
                )
            )
        assert self.web_server.message == 'Save timezone -1'
        assert response == b'HTTP/1.0 303 Moved\r\nLocation: /settings/timezone_form/\r\n\r\n'

        assert restore_timezone() == -1

        # it was tried to get the current time via NTP:
        mock_settime.assert_called_once_with()

        # Request the form:

        response = await self.get_request(
            request_line=b"GET /settings/timezone_form/ HTTP/1.1"
        )
        self.assert_response_parts(
            response,
            parts=(
                'HTTP/1.0 200 OK',
                '<html>',
                '<title>network name-04030201 - OFF</title>',
                '<p>Power switch state: <strong>OFF</strong></p>',
                '<p>Save timezone -1</p>',

                '<input type="number" id="offset" name="offset" min="-12" max="12">',

                '</html>'
            )
        )
        assert self.web_server.message == 'Save timezone -1'
