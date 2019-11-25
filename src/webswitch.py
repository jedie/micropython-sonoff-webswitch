import gc
import sys

import machine
import network
import uasyncio as asyncio
import uos as os
import utime as time
from leds import power_led
from ntp import ntp_sync
from watchdog import watchdog
from wifi import wifi

rtc = machine.RTC()
relay_pin = machine.Pin(12, machine.Pin.OUT, value=0)  # turn replay off
button_pin = machine.Pin(0, machine.Pin.IN)


def send_web_page(writer, message=''):
    yield from writer.awrite('HTTP/1.0 200 OK\r\n')
    yield from writer.awrite('Content-type: text/html; charset=utf-8\r\n')
    yield from writer.awrite('Connection: close\r\n\r\n')

    if relay_pin.value() == 1:
        state = 'ON'
    else:
        state = 'OFF'

    with open('webswitch.html', 'r') as f:
        yield from writer.awrite(f.read().format(
            state=state,
            message=message,

            wifi=wifi,
            ntp_sync=ntp_sync,
            watchdog=watchdog,

            utc=rtc.datetime(),
            alloc=gc.mem_alloc(),
            free=gc.mem_free(),
        ))
    gc.collect()


@asyncio.coroutine
def request_handler(reader, writer):
    print('\nWait for request on %s...' % wifi.station.ifconfig()[0])
    gc.collect()

    address = writer.get_extra_info('peername')
    print('Accepted connection from %s:%s' % address)

    request = yield from reader.read()

    request, body = request.split(b'\r\n\r\n', 1)
    request, headers = request.split(b'\r\n', 1)
    request = request.decode('UTF-8')
    print('request: %r' % request)
    print('headers:', headers)

    body = body.decode('UTF-8')
    print('body: %r' % body)

    method, url, version = request.split(' ', 2)
    print(method, url, version)

    not_found = True
    soft_reset = False
    hard_reset = False

    if method == 'GET':
        if url == '/':
            print('response root page')
            yield from send_web_page(writer, message='')
            not_found = False

        elif url == '/webswitch.css':
            yield from writer.awrite('HTTP/1.0 200 OK\r\n')
            yield from writer.awrite('Content-Type: text/css\r\n')
            yield from writer.awrite('Cache-Control: max-age=6000\r\n')
            yield from writer.awrite('\r\n')
            with open('webswitch.css', 'r') as f:
                yield from writer.awrite(f.read())
            not_found = False

        elif url == '/?power=on':
            relay_pin.value(1)
            yield from send_web_page(writer, message='power on')
            not_found = False

        elif url == '/?power=off':
            relay_pin.value(0)
            yield from send_web_page(writer, message='power off')
            not_found = False

        elif url == '/?soft_reset':
            relay_pin.value(0)
            yield from send_web_page(
                writer,
                message=(
                    'Soft reset device...'
                    ' Restart WebServer by pressing the Button on your device!'
                ))
            print('Soft reset device...')
            soft_reset = True
            not_found = False

        elif url == '/?hard_reset':
            relay_pin.value(0)
            yield from send_web_page(
                writer,
                message=(
                    'Hard reset device...'
                    ' Restart WebServer by pressing the Button on your device!'
                ))
            hard_reset = True
            not_found = False

    if not_found:
        print('not found -> 404')
        yield from writer.awrite('HTTP/1.0 404 Not Found\r\n\r\n')

    yield from writer.aclose()
    gc.collect()

    if hard_reset:
        for no in range(3, 0, -1):
            print('Hard reset device %i wait...' % no)
            time.sleep(1)
        print('Hard reset device...')
        machine.reset()
        sys.exit()

    if soft_reset:
        for no in range(3, 0, -1):
            print('Soft reset device %i wait...' % no)
            time.sleep(1)
        print('Soft reset device...')
        sys.exit()

    watchdog.feed()


def main():
    s = 1
    while not wifi.is_connected:
        print('Wait for WiFi connection %s sec.' % s)
        time.sleep(s)
        s += 5
        
    print('Start webserver on %s...' % wifi.station.ifconfig()[0])
    loop = asyncio.get_event_loop()

    coro = asyncio.start_server(request_handler, '0.0.0.0', 80)
    loop.create_task(coro)

    gc.collect()

    print('run forever...')
    try:
        loop.run_forever()
    except OSError as e:  # [Errno 12] ENOMEM
        print('ERROR:', e)
        print(' *** hard reset! ***')
        machine.reset()
        sys.exit()

    loop.close()


if __name__ == '__main__':
    main()
