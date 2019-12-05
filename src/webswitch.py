import gc
import sys

import uasyncio as asyncio
from http_send_file import send_file
from http_utils import HTTP_LINE_200, send_redirect
from pins import Pins
from rtc import rtc_isoformat
from template import render
from watchdog import WATCHDOG_TIMEOUT


class WebServer:
    def __init__(self, watchdog, version):
        self.watchdog = watchdog
        self.version = version
        self.message = 'Web server started...'
        self.minimal_modules = tuple(sys.modules.keys())

    async def error_redirect(self, writer, message):
        self.message = str(message)
        await send_redirect(writer)

    async def send_html_page(self, writer, filename, content_iterator=None):
        await writer.awrite(HTTP_LINE_200)
        await writer.awrite(b'Content-type: text/html; charset=utf-8\r\n\r\n')

        alloc = gc.mem_alloc() / 1024
        free = gc.mem_free() / 1024

        gc.collect()

        content = render(
            filename=filename,
            context={
                'version': self.version,
                'state': Pins.relay.state,
                'message': self.message,
                'total': alloc + free,
                'alloc': alloc,
                'free': free,
                'utc': rtc_isoformat(sep=' '),
            },
            content_iterator=content_iterator
        )
        for line in content:
            await writer.awrite(line)
        gc.collect()

    async def call_module_func(self, url, method, querystring, reader, writer):
        url = url.strip('/')
        try:
            module_name, func_name = url.split('/')
        except ValueError:
            raise ValueError('URL unknown')

        module_name = 'http_%s' % module_name
        try:
            module = __import__(module_name)
        except ImportError:
            raise ImportError('%s.py not found' % module_name)

        func_name = '%s_%s' % (method.lower(), func_name)
        func = getattr(module, func_name, None)
        if func is None:
            raise AttributeError('Not found: %s.%s' % (module_name, func_name))

        await func(self, reader, writer, querystring)
        del func
        del module
        del sys.modules[module_name]
        gc.collect()

    def parse_request(self, request):
        request, body = request.split(b'\r\n\r\n', 1)
        request, headers = request.split(b'\r\n', 1)
        request = request.decode('UTF-8')
        print('request: %r' % request)
        print('headers:', headers)

        method, url, version = request.split(' ', 2)

        if '?' not in url:
            querystring = None
        else:
            url, querystring = url.split('?', 1)

        return method, url, querystring

    async def send_response(self, reader, writer):
        print('\nAccepted connection from:', writer.get_extra_info('peername'))

        method, url, querystring = self.parse_request(request=await reader.read())
        gc.collect()

        if url == '/':
            await send_redirect(writer)
        elif '.' in url:
            await send_file(self, reader, writer, url)
        else:
            await self.call_module_func(url, method, querystring, reader, writer)
            for module_name in [
                    name for name in sys.modules.keys() if name not in self.minimal_modules]:
                print('remove obsolete module: %r' % module_name)
                del sys.modules[module_name]

        gc.collect()

    async def request_handler(self, reader, writer):
        Pins.power_led.off()
        gc.collect()
        try:
            await self.send_response(reader, writer)
        except Exception as e:
            sys.print_exception(e)
            await self.error_redirect(writer, message=e)
            await asyncio.sleep(3)
            gc.collect()
            if isinstance(e, MemoryError):
                from reset import ResetDevice
                ResetDevice(reason='MemoryError: %s' % e).schedule(period=5000)
        await writer.aclose()
        gc.collect()
        Pins.power_led.on()

    async def feed_watchdog(self):
        while True:
            await asyncio.sleep(int(WATCHDOG_TIMEOUT / 2))
            self.watchdog.feed()

    def run(self):
        loop = asyncio.get_event_loop()
        loop.create_task(asyncio.start_server(self.request_handler, '0.0.0.0', 80))
        loop.create_task(self.feed_watchdog())

        gc.collect()

        Pins.power_led.on()
        print(self.message)
        loop.run_forever()
