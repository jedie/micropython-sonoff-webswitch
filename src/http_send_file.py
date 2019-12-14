import constants
import uos


async def send_file(server, reader, writer, url):
    print('send file:', url)
    url = url.lstrip('/')
    ext = url.rsplit('.', 1)[1]

    mime_type = constants.MIME_TYPES.get(ext, None)
    if mime_type is None:
        from http_utils import send_error
        await send_error(writer, reason='File type unknown!', http_code=404)
        return

    try:
        uos.stat(url)  # Check if file exists
    except OSError:
        from http_utils import send_error
        await send_error(writer, reason='File not found!', http_code=404)
        return

    with open(url, 'rb') as f:
        await writer.awrite(constants.HTTP_LINE_200)
        await writer.awrite(constants.CONTENT_TYPE % mime_type)
        await writer.awrite(constants.HTTP_LINE_CACHE)
        await writer.awrite(b'\r\n')

        while True:
            count = f.readinto(constants.BUFFER, constants.CHUNK_SIZE)
            if count < constants.CHUNK_SIZE:
                await writer.awrite(constants.BUFFER[:count])
                break
            else:
                await writer.awrite(constants.BUFFER)
