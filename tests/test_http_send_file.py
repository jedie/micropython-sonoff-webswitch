from unittest import mock

from tests.base import WebServerTestCase
from tests.utils.open_mock import MockOpen


class HttpSendFileTestCase(WebServerTestCase):
    async def test_unknown_file_extension(self):
        response = await self.get_request(
            request_line=b"GET /foo.bar HTTP/1.1"
        )
        assert response == (
            b'HTTP/1.0 404\r\n'
            b'Content-type: text/plain; charset=utf-8\r\n\r\n'
            b'File type unknown!'
        )

    async def test_file_not_found(self):
        response = await self.get_request(
            request_line=b"GET /not-existing-stylesheet.css HTTP/1.1"
        )
        assert response == (
            b'HTTP/1.0 404\r\n'
            b'Content-type: text/plain; charset=utf-8\r\n\r\n'
            b'File not found!'
        )

    async def test_get_css(self):
        mock_open = MockOpen(open)
        with mock.patch('builtins.open', mock_open) as m:
            response = await self.get_request(
                request_line=b"GET /webswitch.css HTTP/1.1"
            )

        assert response.startswith(
            b'HTTP/1.0 200 OK\r\nContent-Type: text/css\r\nCache-Control: max-age=6000\r\n\r\n'
        )

        data = response.split(b'\r\n\r\n', 1)[1]
        print('-' * 100)
        print(data)
        print('-' * 100)

        with open('webswitch.css', 'rb') as f:
            content = f.read()

        assert data == content

    async def test_get_ico(self):
        mock_open = MockOpen(open)
        with mock.patch('builtins.open', mock_open) as m:
            response = await self.get_request(
                request_line=b"GET /favicon.ico HTTP/1.1"
            )

        headers, data = response.split(b'\r\n\r\n')

        assert headers == (
            b'HTTP/1.0 200 OK\r\nContent-Type: image/x-icon\r\nCache-Control: max-age=6000'
        )

        print('-' * 100)
        print(data)
        print('-' * 100)

        with open('favicon.ico', 'rb') as f:
            content = f.read()

        assert data == content
