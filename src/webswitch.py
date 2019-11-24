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


print('wifi:', wifi)
print('ntp_sync:', ntp_sync)
print('power_led:', power_led)
print('watchdog:', watchdog)


def garbage_collection():
    print('Run a garbage collection:', end='')
    alloced = gc.mem_alloc()
    gc.collect()
    freed = alloced - gc.mem_alloc()
    free = gc.mem_free()
    print('Freed: %i Bytes (now %i Bytes free)' % (freed, free))
    return freed, free


STYLES = '''
html{text-align: center;font-size: 1.3em;}
.button{
  background-color: #e7bd3b; border: none;
  border-radius: 4px; color: #fff; padding: 16px 40px; cursor: pointer;
}
.button2{background-color: #4286f4;}
'''


HTML = '''<html>
<head>
    <title>Sonoff S20 - ESP Web Server</title>
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <link rel="stylesheet" href="/styles.css" type="text/css">
</head>
<body>
    <h1>Sonoff S20 - ESP Web Server</h1>
    <p>state: <strong>{state}</strong></p>
    <p>{message}</p>
    <p>
        <a href="/?power=on"><button class="button">ON</button></a>
        <a href="/?power=off"><button class="button button2">OFF</button></a>
    </p>
    <p>
        <a href="/?soft_reset"><button class="button">Soft reset Device</button></a>
        <a href="/?hard_reset"><button class="button">Hard reset Device</button></a>
    </p>
    <p>{wifi}</p>
    <p>{ntp_sync}</p>
    <p>{watchdog}</p>
    <p><small>
        {alloc}bytes of heap RAM that are allocated<br>
        {free}bytes of available heap RAM (-1 == amount is not known)<br>
        Server time in UTC: {utc}
    </small></p>
</body>
</html>
'''


def send_web_page(writer, message=''):
    yield from writer.awrite('HTTP/1.0 200 OK\r\n')
    yield from writer.awrite('Content-type: text/html; charset=utf-8\r\n')
    yield from writer.awrite('Connection: close\r\n\r\n')

    if relay_pin.value() == 1:
        state = 'ON'
    else:
        state = 'OFF'

    yield from writer.awrite(HTML.format(
        state=state,
        message=message,

        wifi=wifi,
        ntp_sync=ntp_sync,
        watchdog=watchdog,

        utc=rtc.datetime(),
        alloc=gc.mem_alloc(),
        free=gc.mem_free(),
    ))
    garbage_collection()


@asyncio.coroutine
def request_handler(reader, writer):
    print('\nWait for request...')
    garbage_collection()

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

        elif url == '/styles.css':
            yield from writer.awrite('HTTP/1.0 200 OK\r\n')
            yield from writer.awrite('Content-Type: text/css\r\n')
            yield from writer.awrite('Cache-Control: max-age=6000\r\n')
            yield from writer.awrite('\r\n')
            yield from writer.awrite(STYLES)
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
    garbage_collection()

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
    print('start webserver...')

    loop = asyncio.get_event_loop()

    coro = asyncio.start_server(request_handler, '0.0.0.0', 80)
    loop.create_task(coro)

    garbage_collection()

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
