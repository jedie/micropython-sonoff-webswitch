import gc

import constants


async def send_redirect(writer, url='/main/menu/'):
    print('redirect to: %r' % url, end=' ')
    await writer.awrite(constants.HTTP_LINE_303)
    await writer.awrite(constants.HTTP_LINE_LOCATION.format(url=url))
    gc.collect()
    print('OK')


async def send_error(writer, reason, http_code=404):
    print('%s -> %i' % (reason, http_code), end=' ')
    await writer.awrite(b'HTTP/1.0 %i\r\n' % http_code)
    await writer.awrite(b'Content-type: text/plain; charset=utf-8\r\n\r\n')
    await writer.awrite(str(reason))
    gc.collect()
    print('OK')


async def parse_request(reader):
    method, url, http_version = (await reader.readline()).decode().strip().split()
    print(method, url, http_version)

    if '?' in url:
        url, querystring = url.split('?', 1)
    else:
        querystring = None

    # Consume all headers but use only content-length
    content_length = None
    while True:
        line = await reader.readline()
        if line == b'\r\n':
            break  # header ends

        try:
            header, value = line.split(b':', 1)
        except ValueError:
            break

        value = value.strip()

        if header == b'Content-Length':
            content_length = int(value.decode())

        # print(header, value)

    print('content length:', content_length)

    # get body
    if content_length:
        body = (await reader.read(content_length)).decode()
    else:
        body = None

    return method, url, querystring, body
