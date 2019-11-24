import gc
import sys

try:
    import machine
    ON_ESP = True
except ImportError:
    ON_ESP = False
    PORT = 8080
    import os
    import asyncio
    import datetime
    import time

    class FakeRtc:
        def datetime(self):
            return datetime.datetime.utcnow()
    rtc = FakeRtc()
else:
    PORT = 80
    import uos as os
    import uasyncio as asyncio
    import utime as time
    import network

    rtc = machine.RTC()
    relay_pin = machine.Pin(12, machine.Pin.OUT, value=0)  # turn replay off
    button_pin = machine.Pin(0, machine.Pin.IN)


def garbage_collection():
    if not ON_ESP:
        return

    print('Run a garbage collection:', end='')
    alloced = gc.mem_alloc()
    gc.collect()
    freed = alloced - gc.mem_alloc()
    free = gc.mem_free()
    print('Freed: %i Bytes (now %i Bytes free)' % (freed, free))
    return freed, free


def get_wifi_ip():
    if not ON_ESP:
        return '127.0.0.1'

    for interface_type in (network.AP_IF, network.STA_IF):
        interface = network.WLAN(interface_type)
        if interface.active():
            if interface_type == network.AP_IF:
                print('WiFi access point is active!')
            return interface.ifconfig()[0]

    print('ERROR: WiFi not connected!')
    print('Hint: boot.py / main.py should create WiFi connection!')
    raise RuntimeError('No WiFi connection!')


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
    <p><small>
        {alloc}bytes of heap RAM that are allocated<br>
        {free}bytes of available heap RAM (-1 == amount is not known)<br>
        Server time in UTC: {utc}
    </small></p>
</body>
</html>
'''


def get_debounced_value(pin):
    """get debounced value from pin by waiting for 20 msec for stable value"""
    cur_value = pin.value()
    stable = 0
    while stable < 20:
        if pin.value() == cur_value:
            stable = stable + 1
        else:
            stable = 0
            cur_value = pin.value()
    time.sleep_ms(1)
    return cur_value


def button_pressed(pin):
    print('button pressed...')
    cur_button_value = get_debounced_value(pin)
    if cur_button_value == 1:
        if relay_pin.value() == 1:
            print('turn off by button.')
            relay_pin.value(0)
        else:
            print('turn on by button.')
            relay_pin.value(1)

        garbage_collection()


if ON_ESP:
    button_pin.irq(button_pressed)


def send_web_page(writer, message=''):
    yield from writer.awrite('HTTP/1.0 200 OK\r\n')
    yield from writer.awrite('Content-type: text/html; charset=utf-8\r\n')
    yield from writer.awrite('Connection: close\r\n\r\n')

    # yield from writer.awrite('OK %s' % repr(rtc.datetime()))
    # return

    if not ON_ESP:
        state = "NOT ON ESP"
        utc = 0,
        alloc = 0
        free = 0
    else:
        if relay_pin.value() == 1:
            state = 'ON'
        else:
            state = 'OFF'
        utc = rtc.datetime()
        alloc = gc.mem_alloc()
        free = gc.mem_free()

    yield from writer.awrite(HTML.format(
        state=state,
        message=message,
        utc=utc,
        alloc=alloc,
        free=free,
    ))
    if ON_ESP:
        garbage_collection()


@asyncio.coroutine
def request_handler(reader, writer):
    print('\nWait for request...')

    if ON_ESP:
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
            if ON_ESP:
                relay_pin.value(1)
            yield from send_web_page(writer, message='power on')
            not_found = False

        elif url == '/?power=off':
            if ON_ESP:
                relay_pin.value(0)
            yield from send_web_page(writer, message='power off')
            not_found = False

        elif url == '/?soft_reset':
            if ON_ESP:
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
            if ON_ESP:
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

    if ON_ESP:
        # yield from writer.awrite(response)
        yield from writer.aclose()
        garbage_collection()
    else:
        # writer.write(bytes(response, encoding='UTF-8'))
        yield from writer.drain()
        writer.close()

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


def main():
    ip = get_wifi_ip()

    print('start webserver on http://%s:%s' % (ip, PORT))

    loop = asyncio.get_event_loop()

    coro = asyncio.start_server(request_handler, ip, PORT)
    loop.create_task(coro)

    if ON_ESP:
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
