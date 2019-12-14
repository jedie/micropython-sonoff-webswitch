import gc
import sys

import constants
import uasyncio


class WebServer:
    def __init__(self, power_timer, watchdog, version):
        self.power_timer = power_timer
        self.watchdog = watchdog
        self.version = version
        self.message = 'Web server started...'
        self.minimal_modules = tuple(sorted(sys.modules.keys()))

    async def send_html_page(self, writer, filename, content_iterator=None):
        await writer.awrite(constants.HTTP_LINE_200)
        await writer.awrite(b'Content-type: text/html; charset=utf-8\r\n\r\n')

        alloc = gc.mem_alloc() / 1024
        free = gc.mem_free() / 1024

        gc.collect()

        from timezone import localtime_isoformat
        localtime = localtime_isoformat(sep=' ')

        del localtime_isoformat
        del sys.modules['timezone']
        gc.collect()

        from device_name import get_device_name
        device_name = get_device_name()

        del get_device_name
        del sys.modules['device_name']
        gc.collect()

        from pins import Pins
        from template import render

        content = render(
            filename=filename,
            context={
                'version': self.version,
                'device_name': device_name,
                'state': Pins.relay.state,
                'next_switch': self.power_timer.info_text(),
                'message': self.message,
                'total': alloc + free,
                'alloc': alloc,
                'free': free,
                'localtime': localtime,
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

    async def send_response(self, reader, writer):
        print('\nRequest from:', writer.get_extra_info('peername'))

        from http_utils import parse_request
        try:
            method, url, querystring, body = await parse_request(reader)
        except ValueError as e:
            self.message = str(e)
            url = '/'  # redirect

        del parse_request
        del sys.modules['http_utils']
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
            self.message = str(e)
            from http_utils import send_redirect
            await send_redirect(writer)
            await uasyncio.sleep(3)
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
            await uasyncio.sleep(sleep_time)
            self.watchdog.feed()

    def run(self):
        loop = uasyncio.get_event_loop()
        loop.create_task(uasyncio.start_server(self.request_handler, '0.0.0.0', 80))
        loop.create_task(self.feed_watchdog())

        gc.collect()

        from pins import Pins
        Pins.power_led.on()
        print(self.message)
        loop.run_forever()
