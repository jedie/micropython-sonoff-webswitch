import gc

import uasyncio as asyncio
from utils import ResetDevice

HTTP_LINE_200 = b'HTTP/1.0 200 OK\r\n'
HTTP_LINE_303 = b'HTTP/1.1 303 Moved\r\n'
HTTP_LINE_LOCATION = b'Location: /\r\n'
HTTP_LINE_CACHE = b'Cache-Control: max-age=6000\r\n'


class WebServer:
    def __init__(self, pins, rtc, watchdog, version):
        self.pins = pins
        self.rtc = rtc
        self.watchdog = watchdog
        self.version = version
        self.message = 'Web server started...'

    def run(self):
        print('Start web server...')
        loop = asyncio.get_event_loop()
        loop.create_task(asyncio.start_server(self.request_handler, '0.0.0.0', 80))

        gc.collect()

        self.pins.power_led.on()
        loop.run_forever()

    async def send_redirect(self, writer):
        await writer.awrite(HTTP_LINE_303)
        await writer.awrite(HTTP_LINE_LOCATION)
        await writer.awrite(b'\r\n')

    async def send_web_page(self, writer):
        await writer.awrite(HTTP_LINE_200)
        await writer.awrite(b'Content-type: text/html; charset=utf-8\r\n')
        await writer.awrite(b'\r\n')

        alloc = gc.mem_alloc() / 1024
        free = gc.mem_free() / 1024

        gc.collect()

        context = {
            'version': self.version,
            'state': self.pins.relay.state,
            'message': self.message,

            'watchdog': self.watchdog,
            'rtc_memory': repr(self.rtc.d),

            'total': alloc + free,
            'alloc': alloc,
            'free': free,

            'utc': self.rtc.isoformat(sep=' '),
        }
        gc.collect()
        with open('webswitch.html', 'r') as f:
            while True:
                line = f.readline()
                if not line:
                    break
                gc.collect()
                await writer.awrite(line.format(**context))
                gc.collect()
        gc.collect()

    async def request_handler(self, reader, writer):
        self.pins.power_led.off()
        gc.collect()

        print('Accepted connection from:', writer.get_extra_info('peername'))

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

        not_found = True

        gc.collect()

        if method == 'GET':
            if url == '/':
                print('response root page')
                await self.send_web_page(writer)
                not_found = False

            elif url == '/favicon.ico':
                await writer.awrite(HTTP_LINE_200)
                await writer.awrite(b'Content-Type: image/x-icon\r\n')
                await writer.awrite(HTTP_LINE_CACHE)
                await writer.awrite(b'\r\n')
                with open('favicon.ico', 'rb') as f:
                    await writer.awrite(f.read())
                not_found = False

            elif url == '/webswitch.css':
                await writer.awrite(HTTP_LINE_200)
                await writer.awrite(b'Content-Type: text/css\r\n')
                await writer.awrite(HTTP_LINE_CACHE)
                await writer.awrite(b'\r\n')
                with open('webswitch.css', 'rb') as f:
                    await writer.awrite(f.read())
                not_found = False

            elif url == '/?power=on':
                self.pins.relay.on()
                self.message = 'power on'
                await self.send_redirect(writer)
                not_found = False

            elif url == '/?power=off':
                self.pins.relay.off()
                self.message = 'power off'
                await self.send_redirect(writer)
                not_found = False

            elif url == '/?clear':
                self.rtc.clear()
                self.message = 'RTC RAM cleared'
                await self.send_redirect(writer)
                not_found = False

            elif url == '/?reset':
                self.message = (
                    'Reset device...'
                    ' Restart WebServer by pressing the Button on your device!'
                )
                await self.send_redirect(writer)
                ResetDevice(rtc=self.rtc, reason='Reset via web page').schedule(period=5000)
                not_found = False

        if not_found:
            print('not found -> 404')
            await writer.awrite(b'HTTP/1.0 404 Not Found\r\n')
            await writer.awrite(b'\r\n')

        await writer.aclose()
        gc.collect()

        self.pins.power_led.on()
