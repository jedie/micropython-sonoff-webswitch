import io
from asyncio import StreamReader as _StreamReader


async def sleep(sec):
    pass


class StreamReader(_StreamReader):
    pass


class StreamWriter:
    def __init__(self):
        self.data = io.BytesIO()

    def get_extra_info(self, key):
        assert key == 'peername', f'Unknown key={key!r}'
        return ('127.0.0.1', 0)

    def get_response(self):
        return self.data.getvalue()

    async def awrite(self, data):
        if isinstance(data, memoryview):
            data = bytes(data)

        if isinstance(data, str):
            data = data.encode('UTF-8')

        self.data.write(data)

    async def aclose(self):
        pass
