
import gc
import sys

import constants
import uasyncio
from pins import Pins


class WebServer:
    def __init__(self, context, version):
        self.context = context
        self.version = version
        self.message = 'Web server started...'
        self.context.minimal_modules = tuple(sorted(sys.modules.keys()))

        # don't wait until watchdog calls ntp_sync() and update_power_timer()
        from ntp import ntp_sync
        ntp_sync(context)

        from power_timer import update_power_timer
        update_power_timer(context)

    async def send_html_page(self, writer, filename, content_iterator=None):
        # await writer.awrite(constants.HTTP_LINE_200)
        # await writer.awrite(b'Content-type: text/html; charset=utf-8\r\n\r\n')

        alloc = gc.mem_alloc() / 1024
        free = gc.mem_free() / 1024

        from timezone import localtime_isoformat
        localtime = localtime_isoformat(sep=' ')

        # del localtime_isoformat
        # del sys.modules['timezone']

        from device_name import get_device_name
        device_name = get_device_name()

        # del get_device_name
        # del sys.modules['device_name']

        from template import render

        content = render(
            filename=filename,
            context={
                'version': self.version,
                'device_name': device_name,
                'state': Pins.relay.state,
                'next_switch': self.context.power_timer_info_text,
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

        self.context.watchdog.garbage_collection()

        await func(self, reader, writer, querystring, body)
        # del func
        # del module
        # del sys.modules[module_name]

    async def send_response(self, reader, writer):
        print('Request from:', writer.get_extra_info('peername'))

        from http_utils import parse_request
        try:
            method, url, querystring, body = await parse_request(reader)
        except ValueError as e:
            self.message = str(e)
            url = '/'  # redirect

        # del parse_request
        # del sys.modules['http_utils']

        if url == '/':
            from http_utils import send_redirect
            await send_redirect(writer)
        elif '.' in url:
            from http_send_file import send_file
            await send_file(self, reader, writer, url)
        else:
            await self.call_module_func(url, method, querystring, body, reader, writer)

    async def request_handler(self, reader, writer):
        Pins.power_led.off()
        print('__________________________________________________________________________________')
        try:
            await self.send_response(reader, writer)
        except Exception as e:
            sys.print_exception(e)
            self.message = str(e)
            from http_utils import send_redirect
            await send_redirect(writer)
            await uasyncio.sleep(3)

            if isinstance(e, MemoryError):
                from reset import ResetDevice
                ResetDevice(reason='MemoryError: %s' % e).schedule(period=5000)
        await writer.aclose()

        self.context.watchdog.garbage_collection()
        Pins.power_led.on()
        print('----------------------------------------------------------------------------------')

    async def feed_watchdog(self):
        sleep_time = int(constants.WATCHDOG_TIMEOUT / 2)
        while True:
            await uasyncio.sleep(sleep_time)
            self.context.watchdog.feed()

    def run(self):
        loop = uasyncio.get_event_loop()
        loop.create_task(uasyncio.start_server(self.request_handler, '0.0.0.0', 80))
        loop.create_task(self.feed_watchdog())

        from led_dim_level_cfg import restore_power_led_level
        Pins.power_led.on()
        restore_power_led_level()
        # del restore_power_led_level
        # del sys.modules['led_dim_level_cfg']

        print(self.message)
        loop.run_forever()
