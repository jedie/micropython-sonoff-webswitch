import gc
import sys

import constants
import machine
import uasyncio as asyncio
import utime as time
from leds import power_led, relay
from rtc_memory import rtc_memory
from watchdog import watchdog
from wifi import wifi

power_led.off()

rtc = machine.RTC()

button_pin = machine.Pin(0, machine.Pin.IN)


def reset():
    print('Hard reset device wait with flash LED...')
    power_led.flash(sleep=0.2, count=20)
    print('Hard reset device...')
    time.sleep(1)
    machine.reset()
    time.sleep(1)
    sys.exit()


def schedule_reset(period=5000):
    timer = machine.Timer(-1)
    timer.init(
        mode=machine.Timer.ONE_SHOT,
        period=period,
        callback=reset()
    )


def send_web_page(writer, message=''):
    yield from writer.awrite('HTTP/1.0 200 OK\r\n')
    yield from writer.awrite('Content-type: text/html; charset=utf-8\r\n')
    yield from writer.awrite('Connection: close\r\n\r\n')

    alloc = gc.mem_alloc() / 1024
    free = gc.mem_free() / 1024

    # uname = os.uname()

    gc.collect()

    context = {
        'state': relay.state,
        'message': message,

        # 'wifi': wifi,
        # 'ntp_sync': ntp_sync,
        'watchdog': watchdog,
        'rtc_memory': rtc_memory.d,

        # 'nodename': uname.nodename,
        # 'id': ':'.join(['%02x' % char for char in reversed(machine.unique_id())]),
        # 'machine': uname.machine,
        # 'release': uname.release,
        # 'version': uname.version,
        #
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
            yield from writer.awrite(line.format(**context))
            gc.collect()
    gc.collect()


async def request_handler(reader, writer):
    power_led.off()

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

    gc.collect()

    if method == 'GET':
        if url == '/':
            print('response root page')
            yield from send_web_page(writer, message='')
            not_found = False

        elif url == '/favicon.ico':
            yield from writer.awrite('HTTP/1.0 200 OK\r\n')
            yield from writer.awrite('Content-Type: image/x-icon\r\n')
            yield from writer.awrite('Cache-Control: max-age=6000\r\n')
            yield from writer.awrite('\r\n')
            with open('favicon.ico', 'rb') as f:
                yield from writer.awrite(f.read())
            not_found = False

        elif url == '/webswitch.css':
            yield from writer.awrite('HTTP/1.0 200 OK\r\n')
            yield from writer.awrite('Content-Type: text/css\r\n')
            yield from writer.awrite('Cache-Control: max-age=6000\r\n')
            yield from writer.awrite('\r\n')
            with open('webswitch.css', 'rb') as f:
                yield from writer.awrite(f.read())
            not_found = False

        elif url == '/?power=on':
            relay.on()
            yield from send_web_page(writer, message='power on')
            not_found = False

        elif url == '/?power=off':
            relay.off()
            yield from send_web_page(writer, message='power off')
            not_found = False

        elif url == '/?clear':
            rtc_memory.clear()
            yield from send_web_page(writer, message='RTC RAM cleared')
            not_found = False

        elif url == '/?check_fw':
            import esp
            check = esp.check_fw()
            if check:
                message = 'esp.check_fw(): OK'
            else:
                message = 'Firmware error! Please check: esp.check_fw() !'
            yield from send_web_page(writer, message=message)
            not_found = False

        elif url == '/?ota_update':
            print('Set OTA update RTC RAM trigger...')

            # Save to RTC RAM:
            rtc_memory.save(data={
                constants.RTC_KEY_RESET_REASON: 'OTA Update via web page',
                'run': 'ota-update',  # triggered in main.py
            })

            yield from send_web_page(writer, message='Run OTA Update after device reset...')
            schedule_reset()
            not_found = False

        elif url == '/?reset':
            relay.off()

            # Save to RTC RAM:
            rtc_memory.save(data={constants.RTC_KEY_RESET_REASON: 'Reset via web page'})

            yield from send_web_page(
                writer,
                message=(
                    'Reset device...'
                    ' Restart WebServer by pressing the Button on your device!'
                ))
            schedule_reset()
            not_found = False

    if not_found:
        print('not found -> 404')
        yield from writer.awrite('HTTP/1.0 404 Not Found\r\n\r\n')

    yield from writer.aclose()
    gc.collect()

    power_led.on()


# Start Webserver:

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
power_led.on()
loop.run_forever()
