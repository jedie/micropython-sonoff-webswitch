import gc
import sys

import constants
import machine
import uasyncio as asyncio
import utime as time
from leds import power_led, relay
from rtc_memory import rtc_memory

power_led.off()

rtc = machine.RTC()

button_pin = machine.Pin(0, machine.Pin.IN)
HTTP_LINE_200 = b'HTTP/1.0 200 OK\r\n'
HTTP_LINE_CACHE = b'Cache-Control: max-age=6000\r\n'


def reset():
    print('Hard reset device...')
    power_led.off()
    time.sleep(1)
    machine.reset()
    time.sleep(1)
    sys.exit()


def schedule_reset(period=2000):
    timer = machine.Timer(-1)
    timer.init(
        mode=machine.Timer.ONE_SHOT,
        period=period,
        callback=reset
    )


class WebServer:
    def __init__(self, watchdog):
        self.watchdog = watchdog

    def run(self):
        print('Start web server...')
        loop = asyncio.get_event_loop()
        loop.create_task(asyncio.start_server(self.request_handler, '0.0.0.0', 80))

        gc.collect()

        power_led.on()
        loop.run_forever()

    async def send_web_page(self, writer, message=''):
        await writer.awrite(HTTP_LINE_200)
        await writer.awrite(b'Content-type: text/html; charset=utf-8\r\n')
        await writer.awrite(b'\r\n')

        alloc = gc.mem_alloc() / 1024
        free = gc.mem_free() / 1024

        gc.collect()

        context = {
            'state': relay.state,
            'message': message,

            'watchdog': self.watchdog,
            'rtc_memory': rtc_memory.d,

            'total': alloc + free,
            'alloc': alloc,
            'free': free,

            'utc': rtc.datetime(),
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
        power_led.off()
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
                await self.send_web_page(writer, message='')
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
                relay.on()
                await self.send_web_page(writer, message='power on')
                not_found = False

            elif url == '/?power=off':
                relay.off()
                await self.send_web_page(writer, message='power off')
                not_found = False

            elif url == '/?clear':
                rtc_memory.clear()
                await self.send_web_page(writer, message='RTC RAM cleared')
                not_found = False

            elif url == '/?ota_update':
                print('Set OTA update RTC RAM trigger...')

                # Save to RTC RAM:
                rtc_memory.save(data={
                    constants.RTC_KEY_RESET_REASON: 'OTA Update via web page',
                    'run': 'ota-update',  # triggered in main.py
                })

                await self.send_web_page(writer, message='Run OTA Update after device reset...')
                schedule_reset()
                not_found = False

            elif url == '/?reset':
                relay.off()

                # Save to RTC RAM:
                rtc_memory.save(data={constants.RTC_KEY_RESET_REASON: 'Reset via web page'})

                await self.send_web_page(
                    writer,
                    message=(
                        'Reset device...'
                        ' Restart WebServer by pressing the Button on your device!'
                    ))
                schedule_reset()
                not_found = False

        if not_found:
            print('not found -> 404')
            await writer.awrite(b'HTTP/1.0 404 Not Found\r\n')
            await writer.awrite(b'\r\n')

        await writer.aclose()
        gc.collect()

        power_led.on()
