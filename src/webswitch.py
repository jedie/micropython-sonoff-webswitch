import gc
import sys

import uasyncio as asyncio
from http_send_file import send_file
from http_utils import (HTTP_LINE_200, querystring2dict, send_error,
                        send_redirect)
from watchdog import WATCHDOG_TIMEOUT


class WebServer:
    def __init__(self, pins, rtc, watchdog, auto_timer, version):
        self.pins = pins
        self.rtc = rtc
        self.watchdog = watchdog
        self.auto_timer = auto_timer
        self.version = version
        self.message = 'Web server started...'

    async def error_redirect(self, writer, message):
        self.message = message
        await send_redirect(writer)

    async def send_html_page(self, writer, filename, context):
        await writer.awrite(HTTP_LINE_200)
        await writer.awrite(b'Content-type: text/html; charset=utf-8\r\n\r\n')

        alloc = gc.mem_alloc() / 1024
        free = gc.mem_free() / 1024

        gc.collect()

        context.update({
            'version': self.version,
            'message': self.message,
            'total': alloc + free,
            'alloc': alloc,
            'free': free,
            'utc': self.rtc.isoformat(sep=' '),
        })
        gc.collect()
        with open(filename, 'r') as f:
            while True:
                line = f.readline()
                if not line:
                    break
                gc.collect()
                await writer.awrite(line.format(**context))
                gc.collect()
        gc.collect()

    async def call_module_func(self, url, method, get_parameters, reader, writer):
        url = url.strip('/')
        try:
            module_name, func_name = url.split('/')
        except ValueError:
            await send_error(writer, 'URL unknown')
            return
        module_name = 'http_%s' % module_name
        func_name = '%s_%s' % (method.lower(), func_name)
        print('func: %s.%s' % (module_name, func_name))
        try:
            module = __import__(module_name)
        except ImportError:
            await send_error(writer, '%s.py not found' % module_name)
            return

        func = getattr(module, func_name, None)
        if func is None:
            await send_error(writer, 'Not found: %s.%s' % (module_name, func_name))
            return

        await func(self, reader, writer, get_parameters)
        del sys.modules[module_name]

    async def send_response(self, reader, writer):
        print('\nAccepted connection from:', writer.get_extra_info('peername'))

        request = await reader.read()

        request, body = request.split(b'\r\n\r\n', 1)
        request, headers = request.split(b'\r\n', 1)
        request = request.decode('UTF-8')
        print('request: %r' % request)
        print('headers:', headers)

        # body = body.decode('UTF-8')
        # print('body: %r' % body)

        method, url, version = request.split(' ', 2)
        print(method, url, version)

        if '?' not in url:
            get_parameters = None
        else:
            url, get_parameters = url.split('?', 1)
            get_parameters = querystring2dict(get_parameters)

        gc.collect()
        if url == '/':
            print('response root page')
            await send_redirect(writer)
        elif '.' in url:
            await send_file(self, reader, writer, url)
        else:
            try:
                await self.call_module_func(url, method, get_parameters, reader, writer)
            except Exception as e:
                sys.print_exception(e)
                await self.error_redirect(writer, message='Command error: %s' % e)
        gc.collect()

    async def request_handler(self, reader, writer):
        self.pins.power_led.off()
        gc.collect()
        try:
            await self.send_response(reader, writer)
        except Exception as e:
            sys.print_exception(e)
            await send_error(writer, reason=e, http_code=500)
        await writer.aclose()
        gc.collect()
        self.pins.power_led.on()

    async def feed_watchdog(self):
        while True:
            await asyncio.sleep(int(WATCHDOG_TIMEOUT / 2))
            self.watchdog.feed()

    def run(self):
        loop = asyncio.get_event_loop()
        loop.create_task(asyncio.start_server(self.request_handler, '0.0.0.0', 80))
        loop.create_task(self.feed_watchdog())

        gc.collect()

        self.pins.power_led.on()
        print(self.message)
        loop.run_forever()
