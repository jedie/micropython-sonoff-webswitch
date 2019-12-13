import gc
import sys

import uasyncio as asyncio

_HEX = '0123456789ABCDEF'

_HTML_PREFIX = b"""
<html>
<head><title>Minimal MicroPython Webserver</title></head>
<body>
    <h1>Minimal MicroPython Webserver</h1>
    <pre>
"""
_HTML_SUFFIX = b"""
    </pre>
    <hr>
    <h2>POST test form:</h2>
    <form action="/test/post/" method="post">
        <textarea name="text" rows="4" cols="20">POST text
from textarea!</textarea>
        <p>
            <input type="checkbox" id="c1" name="c1" checked><label for="c1">c1</label>
            <input type="checkbox" id="c2" name="c2"><label for="c2">c2</label>
        </p>
        <input type="submit">
    </form>
    <hr>
    <h2>GET test form:</h2>
    <form action="/test/get/" method="get">
        <textarea name="text" rows="4" cols="20">GET text
from textarea!</textarea>
        <p>
            <input type="checkbox" id="c1" name="c1"><label for="c1">c1</label>
            <input type="checkbox" id="c2" name="c2" checked><label for="c2">c2</label>
        </p>
        <input type="submit">
    </form>
    <hr>
    <p>
"""
_HTML_FOOTER = """
    </p>
</body>"""


def unquote(string):
    string = string.replace('+', ' ')
    if '%' not in string:
        return string

    bits = string.split('%')
    if len(bits) == 1:
        return string

    res = [bits[0]]
    for item in bits[1:]:
        if len(item) >= 2:
            a, b = item[:2].upper()
            if a in _HEX and b in _HEX:
                res.append(chr(int(a + b, 16)))
                res.append(item[2:])
                continue

        res.append('%')
        res.append(item)

    return ''.join(res)


def parse_qsl(qs):
    if qs is None:
        return ()
    qs = str(qs)
    pairs = [s2 for s1 in qs.split('&') for s2 in s1.split(';')]
    res = []
    for name_value in pairs:
        try:
            name, value = name_value.split('=', 1)
        except ValueError:
            res.append((unquote(name_value), ''))
        else:
            res.append((unquote(name), unquote(value)))
    return res


def request_query2dict(qs):
    return dict(parse_qsl(qs))


class WebServer:
    async def parse_request(self, reader):
        method, url, http_version = (await reader.readline()).decode().strip().split()
        print(method, url, http_version)

        if '?' in url:
            url, querystring = url.split('?', 1)
        else:
            querystring = None

        print('querystring:', repr(querystring))

        # Consume all headers but use only content-length
        content_length = None
        while True:
            line = await reader.readline()
            if line == b'\r\n':
                break  # header ends

            try:
                header, value = line.split(b':', 1)
            except ValueError:
                print('ValueError in:', repr(line))
                break

            value = value.strip()

            if header == b'Content-Length':
                content_length = int(value.decode())

            print(header, value)

        print('content length:', content_length)

        # get body
        if content_length:
            body = (await reader.read(content_length)).decode()
            print('body:', repr(body))
        else:
            body = None

        return method, url, querystring, body

    async def send_response(self, reader, writer):
        peername = writer.get_extra_info('peername')
        print('\nRequest from:', peername)
        await writer.awrite(b'HTTP/1.0 200 OK\r\n')
        await writer.awrite(b'Content-type: text/html; charset=utf-8\r\n\r\n')

        await writer.awrite(_HTML_PREFIX)

        await writer.awrite(b'Your IP: %s port:%s\n' % peername)

        await writer.awrite(b'\n')

        method, url, querystring, body = await self.parse_request(reader)

        await writer.awrite(b'Method: %s\n' % method)
        await writer.awrite(b'URL: %s\n' % url)
        await writer.awrite(b'querystring: %s\n' % querystring)
        await writer.awrite(b'parsed querystring: %s\n' % request_query2dict(querystring))
        await writer.awrite(b'body: %s\n' % body)
        await writer.awrite(b'parsed body: %s\n' % request_query2dict(body))

        await writer.awrite(_HTML_SUFFIX)

        alloc = gc.mem_alloc() / 1024
        free = gc.mem_free() / 1024

        await writer.awrite(
            b'RAM total: {total:.2f} KB, used: {alloc:.2f} KB, free: {free:.2f} KB'.format(
                total=alloc + free,
                alloc=alloc,
                free=free
            )
        )

        await writer.awrite(_HTML_FOOTER)
        await writer.aclose()

    async def request_handler(self, reader, writer):
        await self.send_response(reader, writer)
        gc.collect()

    def run(self):
        loop = asyncio.get_event_loop()
        loop.create_task(asyncio.start_server(self.request_handler, '0.0.0.0', 80))
        print('\nWeb server started...')
        loop.run_forever()


def main():
    from wifi import WiFi
    wifi = WiFi()
    if not wifi.is_connected:
        wifi.ensure_connection()
    del wifi
    del WiFi
    del sys.modules['wifi']
    gc.collect()

    server = WebServer()
    server.run()


if __name__ == '__main__':
    try:
        main()
    except Exception as e:
        sys.print_exception(e)

    print('Hard reset !')

    import machine
    machine.reset()

    import utime
    utime.sleep(1)

    print('sys.exit()')
    import sys
    sys.exit()
