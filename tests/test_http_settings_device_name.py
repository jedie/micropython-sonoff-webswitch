from device_name import get_device_name
from tests.base import WebServerTestCase


class HttpMainMenuTestCase(WebServerTestCase):
    async def test_device_name_not_allowed_characters(self):
        assert get_device_name() == 'network name-04030201'
        response = await self.get_request(
            request_line=(
                b"GET /settings/submit_device_name/?name=Name+with+Spaces! HTTP/1.1"
            )
        )
        assert self.web_server.message == 'Error: Device name contains not allowed characters!'
        assert get_device_name() == 'network name-04030201'
        self.assert_response_parts(
            response,
            parts=(
                'HTTP/1.0 200 OK',
                '<html>',
                '<title>network name-04030201 - OFF</title>',

                '<p>Error: Device name contains not allowed characters!</p>',
                '<input type="text" name="name" value="Name-with-Spaces">',

                '</html>'
            )
        )

    async def test_device_name_empty(self):
        assert get_device_name() == 'network name-04030201'
        response = await self.get_request(
            request_line=(
                b"GET /settings/submit_device_name/ HTTP/1.1"
            )
        )
        assert self.web_server.message == (
            'Error: New Device name is too short. Enter at leased 3 characters!'
        )
        assert get_device_name() == 'network name-04030201'
        self.assert_response_parts(
            response,
            parts=(
                'HTTP/1.0 200 OK', '<html>',
                '<title>network name-04030201 - OFF</title>',

                '<p>Error: New Device name is too short. Enter at leased 3 characters!</p>',
                '<input type="text" name="name" value="network name-04030201">',

                '</html>'
            )
        )

    async def test_device_name_too_short(self):
        assert get_device_name() == 'network name-04030201'
        response = await self.get_request(
            request_line=(
                b"GET /settings/submit_device_name/?name=X HTTP/1.1"
            )
        )
        assert self.web_server.message == (
            'Error: New Device name is too short. Enter at leased 3 characters!'
        )
        assert get_device_name() == 'network name-04030201'
        self.assert_response_parts(
            response,
            parts=(
                'HTTP/1.0 200 OK', '<html>',
                '<title>network name-04030201 - OFF</title>',

                '<p>Error: New Device name is too short. Enter at leased 3 characters!</p>',
                '<input type="text" name="name" value="X">',

                '</html>'
            )
        )

    async def test_set_device_name(self):
        response = await self.get_request(
            request_line=(
                b"GET /settings/submit_device_name/?name=123 HTTP/1.1"
            )
        )
        assert self.web_server.message == "Device name '123' saved."
        assert response == b'HTTP/1.0 303 Moved\r\nLocation: /settings/device_name_form/\r\n\r\n'

        # Request the form:

        response = await self.get_request(
            request_line=b"GET /settings/device_name_form/ HTTP/1.1"
        )
        self.assert_response_parts(
            response,
            parts=(
                'HTTP/1.0 200 OK', '<html>',

                '<title>123 - OFF</title>',
                "<p>Device name '123' saved.</p>",
            )
        )
        assert self.web_server.message == "Device name '123' saved."
