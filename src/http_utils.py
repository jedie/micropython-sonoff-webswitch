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


def parse_qsl(qs):
    """
    Doesn't unquote:
    https://github.com/jedie/micropython-sonoff-webswitch/commit/1e49bdb5220b3e2ee70a6465cf48d3ed2f83445d#diff-22aee1553e4be2795b95ece637d31f7cR29
    """
    pairs = [s2 for s1 in qs.split('&') for s2 in s1.split(';')]
    res = []
    for name_value in pairs:
        try:
            name, value = name_value.split('=', 1)
        except ValueError:
            res.append((name_value, ''))
        else:
            res.append((name, value))
    return res


def querystring2dict(qs):
    return dict(parse_qsl(qs))
