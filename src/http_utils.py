HTTP_LINE_200 = b'HTTP/1.0 200 OK\r\n'
HTTP_LINE_303 = b'HTTP/1.0 303 Moved\r\n'
HTTP_LINE_LOCATION = b'Location: {url}\r\n'
HTTP_LINE_CACHE = b'Cache-Control: max-age=6000\r\n'


async def send_redirect(writer, url='/main/menu/'):
    await writer.awrite(HTTP_LINE_303)
    await writer.awrite(HTTP_LINE_LOCATION.format(url=url))
    await writer.awrite(b'\r\n')


async def send_error(writer, reason, http_code=404):
    print('%s -> %i' % (reason, http_code))
    await writer.awrite(b'HTTP/1.0 %i\r\n' % http_code)
    await writer.awrite(b'Content-type: text/plain; charset=utf-8\r\n\r\n')
    await writer.awrite(str(reason))
