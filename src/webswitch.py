import gc
import sys

import constants
import machine
import network
import ntptime
import utime as time
from leds import power_led
from ntp import ntp_sync
from watchdog import watchdog
from wifi import wifi

rtc = machine.RTC()

try:
    import usocket as socket
except BaseException:
    import socket


relay_pin = machine.Pin(12, machine.Pin.OUT, value=0)  # turn replay off
button_pin = machine.Pin(0, machine.Pin.IN)


rtc = machine.RTC()


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
    <link rel="icon" href="data:,">
    <style>{styles}</style>
</head>
<body>
  <h1>Sonoff S20 - ESP Web Server</h1>
  <p>state: <strong>{state}</strong></p>
  <p>{message}</p>
  <p><a href="/?power=on"><button class="button">ON</button></a></p>
  <p><a href="/?power=off"><button class="button button2">OFF</button></a></p>
  <p><a href="/?soft_reset"><button class="button">Soft reset Device</button></a></p>
  <p><a href="/?hard_reset"><button class="button">Hard reset Device</button></a></p>
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


def get_wifi_ip():
    for interface_type in (network.AP_IF, network.STA_IF):
        interface = network.WLAN(interface_type)
        if interface.active():
            if interface_type == network.AP_IF:
                print('WiFi access point is active!')
            return interface.ifconfig()[0]


def garbage_collection():
    print('Run a garbage collection:', end='')
    alloced = gc.mem_alloc()
    gc.collect()
    freed = alloced - gc.mem_alloc()
    free = gc.mem_free()
    print('Freed: %i Bytes (now %i Bytes free)' % (freed, free))
    return freed, free


class WebSwitch:
    running = False

    def __init__(self):
        self.ip = get_wifi_ip()
        if self.ip is None:
            print('ERROR: WiFi not connected!')
            print('Hint: boot.py / main.py should create WiFi connection!')
            raise RuntimeError('No WiFi connection!')

        print('Start Webserver on:', self.ip)
        garbage_collection()

        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.s.bind(('', 80))
        self.s.listen(0)

    def button_pressed(self, pin):
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

            if not self.running:
                print('Restart Webserver')
                self.main_loop()
            else:
                print('Webserver still running, ok.')

    def send_web_page(self, message=''):
        self.conn.send('HTTP/1.1 200 OK\n')
        self.conn.send('Content-Type: text/html\n')
        self.conn.send('Connection: close\n\n')

        if relay_pin.value() == 1:
            state = 'ON'
        else:
            state = 'OFF'

        self.conn.sendall(HTML.format(
            styles=STYLES,
            state=state,
            message=message,
            utc=rtc.datetime(),
            alloc=gc.mem_alloc(),
            free=gc.mem_free(),
        ))

    def send_redirect(self, url='/'):
        self.conn.send('HTTP/1.1 302 redirect\n')
        self.conn.send('Location: %s\n' % url)

    def handle_one_request(self):
        print('\nWait for connection on:', self.ip)

        power_led.on()
        self.conn, addr = self.s.accept()
        power_led.off()

        print('Connection from IP:', addr[0])

        header = self.conn.recv(1024)
        print('Header:', header)

        request = header.split(b'\r\n')[0].decode('ASCII')
        print('Request: %r' % request)

        url = request.split(' ', 2)[1]
        print('url: %r' % url)

        if url == '/':
            print('response root page')
            self.send_web_page(message='')

        elif url == '/?power=on':
            relay_pin.value(1)
            self.send_web_page(message='power on')

        elif url == '/?power=off':
            relay_pin.value(0)
            self.send_web_page(message='power off')

        elif url == '/?soft_reset':
            relay_pin.value(0)
            self.send_web_page(
                message='Soft reset device... Restart WebServer by pressing the Button on your device!')
            self.conn.close()
            print('Soft reset device...')
            self.running = False

        elif url == '/?hard_reset':
            relay_pin.value(0)
            self.send_web_page(
                message='Hard reset device... Restart WebServer by pressing the Button on your device!')
            self.conn.close()
            for no in range(3, 0, -1):
                print('Hard reset device %i wait...' % no)
                time.sleep(1)
            print('Hard reset device...')
            self.running = False
            machine.reset()

        else:
            print('Error: unknown request: %r' % url)
            self.send_web_page(message='Error: unknown request!')
            # self.conn.send('HTTP/1.1 404 not found\n')
            # self.conn.send('Connection: close\n\n')

        self.conn.close()

    def main_loop(self):
        button_pin.irq(self.button_pressed)

        self.running = True
        while self.running:
            self.handle_one_request()
            print('watchdog 1:', watchdog)
            watchdog.feed()
            print('watchdog 2:', watchdog)
            print('wifi:', wifi)
            print('ntp_sync:', ntp_sync)

        sys.exit()


def main():
    web_switch = WebSwitch()
    web_switch.running = False
    web_switch.main_loop()


if __name__ == '__main__':
    main()
