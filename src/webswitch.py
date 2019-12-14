import gc
import sys

import constants
import uasyncio as asyncio


class WebServer:
    def __init__(self, power_timer, watchdog, version):
        self.power_timer = power_timer
        self.watchdog = watchdog
        self.version = version
        self.message = 'Web server started...'
        self.minimal_modules = tuple(sorted(sys.modules.keys()))

    async def error_redirect(self, writer, message):
        self.message = str(message)
        from http_utils import send_redirect
        await send_redirect(writer)

    async def send_html_page(self, writer, filename, content_iterator=None):
        from http_utils import HTTP_LINE_200
        await writer.awrite(HTTP_LINE_200)
        await writer.awrite(b'Content-type: text/html; charset=utf-8\r\n\r\n')

        alloc = gc.mem_alloc() / 1024
        free = gc.mem_free() / 1024

        gc.collect()

        from template import render
        from timezone import localtime_isoformat
        from pins import Pins
        content = render(
            filename=filename,
            context={
                'version': self.version,
                'state': Pins.relay.state,
                'next_switch': self.power_timer.info_text(),
                'message': self.message,
                'total': alloc + free,
                'alloc': alloc,
                'free': free,
                'localtime': localtime_isoformat(sep=' '),
            },
            content_iterator=content_iterator
        )
        for line in content:
            await writer.awrite(line)
        gc.collect()

    async def call_module_func(self, url, method, querystring, body, reader, writer):
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

        await func(self, reader, writer, querystring, body)
        del func
        del module
        del sys.modules[module_name]
        gc.collect()

    async def parse_request(self, reader):
        method, url, http_version = (await reader.readline()).decode().strip().split()
        # print(http_version)

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

    async def send_response(self, reader, writer):
        print('\nRequest from:', writer.get_extra_info('peername'))

        try:
            method, url, querystring, body = await self.parse_request(reader)
        except ValueError as e:
            self.message = str(e)
            url = '/'  # redirect

        gc.collect()

        if url == '/':
            from http_utils import send_redirect
            await send_redirect(writer)
        elif '.' in url:
            from http_send_file import send_file
            await send_file(self, reader, writer, url)
        else:
            await self.call_module_func(url, method, querystring, body, reader, writer)
            for module_name in [
                    name for name in sys.modules.keys() if name not in self.minimal_modules]:
                print('remove obsolete module: %r' % module_name)
                del sys.modules[module_name]

        gc.collect()

    async def request_handler(self, reader, writer):
        from pins import Pins
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
        sleep_time = int(constants.WATCHDOG_TIMEOUT / 2)
        while True:
            await asyncio.sleep(sleep_time)
            self.watchdog.feed()

    def run(self):
        loop = asyncio.get_event_loop()
        loop.create_task(asyncio.start_server(self.request_handler, '0.0.0.0', 80))
        loop.create_task(self.feed_watchdog())

        gc.collect()

        from pins import Pins
        Pins.power_led.on()
        print(self.message)
        loop.run_forever()
