import gc
import sys

import esp
import uasyncio
import utime
from micropython import const

_HTML_PREFIX = b"""
<html>
<head>
    <title>MicroPython RAM hex viewer Webserver</title>
<style>
    body {
      background-color: linen;
    }

    h1 {
      color: maroon;
      margin-left: 40px;
    }
    #hex {
        font-family: monospace;
    }
</style>
</head>
<body>
    <h1>MicroPython RAM hex viewer Webserver</h1>
"""
_HTML_FOOTER = """
    <hr>
    <form action="/">
        <p>
            <input type="text" id="text" name="text" value="{text}">
            <label for="text">text</label>
        </p>
        <input type="submit">
    </form>
</body>"""


LINE_COUNT = const(32)
CHUNK_SIZE = const(32)
BUFFER = bytearray(CHUNK_SIZE)

TABLE_LINE = '<tr><td>{address}</td><td>{hex}</td><td>{chars}</td></tr>\n'

_HEX = '0123456789ABCDEF'


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


async def hex_dump(writer, offset=0):
    for line_num in range(LINE_COUNT):
        current_offset = offset + (line_num * CHUNK_SIZE)
        try:
            esp.flash_read(current_offset, BUFFER)
        except OSError as e:
            await writer.awrite(b'Error: %s' % e)
            break

        await writer.awrite(TABLE_LINE.format(
            address='%08x - %08x' % (current_offset, current_offset + CHUNK_SIZE - 1),
            hex=' '.join('%02x' % char for char in BUFFER),
            chars=''.join(
                chr(char)
                if 32 <= char <= 126 and char not in (60, 62) else '.'
                for char in BUFFER
            ),
        ))
    gc.collect()


async def search(writer, offset, text):
    print('search for', repr(text))
    next_update = utime.time() + 1
    while True:
        try:
            esp.flash_read(offset, BUFFER)
        except OSError as e:
            await writer.awrite(b'Error: %s' % e)
            break

        if text in BUFFER:
            print('Found in block:', offset)
            await writer.awrite(b'Found in block: %i\n' % offset)
            return offset

        offset += CHUNK_SIZE

        if utime.time() >= next_update:
            print('Search:', offset)
            await writer.awrite(b'Search %i\n' % offset)
            next_update = utime.time() + 1


class WebServer:
    async def parse_request(self, reader):
        method, url, http_version = (await reader.readline()).decode().strip().split()
        print(method, url, http_version)

        if '?' in url:
            url, querystring = url.split('?', 1)
            querystring = request_query2dict(querystring)
        else:
            querystring = {}

        print('querystring:', repr(querystring))

        # Consume all headers
        while True:
            line = await reader.readline()
            if line == b'\r\n':
                break  # header ends

        return method, url, querystring

    async def send_response(self, reader, writer):
        peername = writer.get_extra_info('peername')
        print('\nRequest from:', peername)
        await writer.awrite(b'HTTP/1.0 200 OK\r\n')
        await writer.awrite(b'Content-type: text/html; charset=utf-8\r\n\r\n')

        await writer.awrite(_HTML_PREFIX)

        await writer.awrite(b'Your IP: %s port:%s\n' % peername)

        await writer.awrite(b'\n')

        method, url, querystring = await self.parse_request(reader)

        offset = int(querystring.get('offset', 0))
        print('Current offset:', repr(offset))
        search_text = querystring.get('text', '')
        print('search text:', repr(search_text))

        await writer.awrite(b'<pre>')
        # await writer.awrite(b'Method: %s\n' % method)
        # await writer.awrite(b'URL: %s\n' % url)
        # await writer.awrite(b'querystring: %s\n' % querystring)

        await writer.awrite(b'flash size: {size} Bytes (0x{size:x})\n'.format(
            size=esp.flash_size()
        ))
        await writer.awrite(b'flash user start: {user_start} Bytes (0x{user_start:x})\n'.format(
            user_start=esp.flash_user_start()
        ))

        if search_text:
            await writer.awrite(b'search for: %r\n' % search_text)
            offset = await search(writer, offset, text=search_text.encode('UTF-8'))

        await writer.awrite(b'</pre>')

        await writer.awrite(b'<table id="hex">')

        await hex_dump(writer, offset=offset)
        await writer.awrite(b'</table>')

        back_offset = offset - (LINE_COUNT * CHUNK_SIZE)
        next_offset = offset + (LINE_COUNT * CHUNK_SIZE)
        print('back', back_offset, 'next', next_offset)
        await writer.awrite(
            b'<a href="/?offset={back}">back</a> <a href="/?offset={next}">next</a>'.format(
                back=back_offset,
                next=next_offset,
            )
        )

        alloc = gc.mem_alloc() / 1024
        free = gc.mem_free() / 1024

        await writer.awrite(
            b'<p>RAM total: {total:.2f} KB, used: {alloc:.2f} KB, free: {free:.2f} KB</p>'.format(
                total=alloc + free,
                alloc=alloc,
                free=free
            )
        )
        await writer.awrite(
            b'<p>Render time: %i ms</p>' % utime.ticks_diff(utime.ticks_ms(), self.start_time)
        )

        await writer.awrite(_HTML_FOOTER.format(text=search_text))
        await writer.aclose()

    async def request_handler(self, reader, writer):
        self.start_time = utime.ticks_ms()
        await self.send_response(reader, writer)
        gc.collect()
        # if __debug__:
        #     micropython.mem_info(1)
        print('----------------------------------------------------------------------------------')

    def run(self):
        loop = uasyncio.get_event_loop()
        loop.create_task(uasyncio.start_server(self.request_handler, '0.0.0.0', 80))
        print('\nWeb server started...')
        loop.run_forever()


def main():
    from context import Context

    context = Context

    import wifi
    wifi.init(context)
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

    utime.sleep(1)

    print('sys.exit()')
    import sys
    sys.exit()
