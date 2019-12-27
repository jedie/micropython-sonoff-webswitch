
import gc
import sys

import constants
import micropython
import uasyncio
from pins import Pins


class WebServer:
    def __init__(self, context, version):
        self.context = context
        self.version = version
        self.message = 'Web server started...'
        self.context.minimal_modules = tuple(sorted(sys.modules.keys()))

    async def send_html_page(self, writer, filename, content_iterator=None):
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

        from power_timer import get_info_text
        power_timer_info_text = get_info_text(context=self.context)
        del get_info_text
        del sys.modules['power_timer']
        gc.collect()

        alloc = gc.mem_alloc() / 1024
        free = gc.mem_free() / 1024

        from template import render
        content = render(
            filename=filename,
            context={
                'version': self.version,
                'device_name': device_name,
                'state': Pins.relay.state,
                'next_switch': power_timer_info_text,
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

        gc.collect()

        await func(self, reader, writer, querystring, body)

    async def send_response(self, reader, writer):
        print('Request from:', writer.get_extra_info('peername'))

        from http_utils import parse_request
        try:
            method, url, querystring, body = await parse_request(reader)
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

        gc.collect()

    async def request_handler(self, reader, writer):
        Pins.power_led.off()
        print('__________________________________________________________________________________')
        gc.collect()
        try:
            await self.send_response(reader, writer)
        except Exception as e:
            sys.print_exception(e)
            self.message = str(e)
            from http_utils import send_redirect
            await send_redirect(writer)
            await uasyncio.sleep(3)

            if isinstance(e, MemoryError):
                micropython.mem_info(1)
                from reset import ResetDevice
                ResetDevice(reason='MemoryError: %s' % e).reset()

        print('close writer')
        gc.collect()
        await writer.aclose()

        self.context.watchdog.garbage_collection()
        if __debug__:
            micropython.mem_info(1)
        Pins.power_led.on()
        print('----------------------------------------------------------------------------------')

    async def feed_watchdog(self):
        """
        Start some periodical tasks and feed the watchdog
        """
        sleep_time = int(constants.WATCHDOG_TIMEOUT / 2)
        while True:

            gc.collect()

            from power_timer import update_power_timer
            if update_power_timer(self.context) is not True:
                from reset import ResetDevice
                ResetDevice(reason='Update power timer error').reset()

            del update_power_timer
            del sys.modules['power_timer']
            gc.collect()

            from ntp import ntp_sync
            if ntp_sync(self.context) is not True:
                from reset import ResetDevice
                ResetDevice(reason='NTP sync error').reset()

            del ntp_sync
            del sys.modules['ntp']
            gc.collect()

            self.context.watchdog.feed()

            gc.collect()
            await uasyncio.sleep(sleep_time)

    def run(self):
        loop = uasyncio.get_event_loop()
        loop.create_task(uasyncio.start_server(self.request_handler, '0.0.0.0', 80))
        loop.create_task(self.feed_watchdog())

        from led_dim_level_cfg import restore_power_led_level
        Pins.power_led.on()
        restore_power_led_level()
        del restore_power_led_level
        del sys.modules['led_dim_level_cfg']

        print(self.message)
        loop.run_forever()
