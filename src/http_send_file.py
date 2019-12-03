import uos as os
from http_utils import HTTP_LINE_200, HTTP_LINE_CACHE

_MIME_TYPES = {
    'ico': b'image/x-icon',
    'css': b'text/css',
}
_CONTENT_TYPE = b'Content-Type: %s\r\n'
_CHUNK_SIZE = const(512)


async def send_file(server, reader, writer, url):
    print('send file:', url)
    url = url.lstrip('/')
    ext = url.rsplit('.', 1)[1]

    mime_type = _MIME_TYPES.get(ext, None)
    if mime_type is None:
        await server.send_404_error(writer, reason='File type unknown!')
        return

    try:
        os.stat(url)  # Check if file exists
    except OSError:
        await server.send_404_error(writer, reason='File not found!')
        return

    with open(url, 'rb') as f:
        await writer.awrite(HTTP_LINE_200)
        await writer.awrite(_CONTENT_TYPE % mime_type)
        await writer.awrite(HTTP_LINE_CACHE)
        await writer.awrite(b'\r\n')

        buffer = bytearray(_CHUNK_SIZE)
        while True:
            count = f.readinto(buffer, _CHUNK_SIZE)
            if count < _CHUNK_SIZE:
                await writer.awrite(buffer[:count])
                break
            else:
                await writer.awrite(buffer)
