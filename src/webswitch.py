import gc
import sys
import time

try:
    import usocket as socket
except ImportError:
    import socket

try:
    import machine
    import network
    ON_ESP=True
    PORT=80
except ImportError:
    ON_ESP=False
    PORT=8000

if ON_ESP:
    led_pin = machine.Pin(13, machine.Pin.OUT, value=0)  # turn power LED on
    relay_pin = machine.Pin(12, machine.Pin.OUT, value=0)  # turn replay off
    button_pin = machine.Pin(0, machine.Pin.IN)
    rtc = machine.RTC()


HEX='0123456789ABCDEF'


def unquote(string):
    string=string.replace('+', ' ')
    if '%' not in string:
        return string

    bits = string.split('%')
    if len(bits) == 1:
        return string

    res = [bits[0]]
    for item in bits[1:]:
        if len(item)>=2:
            a, b = item[:2].upper()
            if a in HEX and b in HEX:
                res.append(chr(int(a + b, 16)))
                res.append(item[2:])
                continue

        res.append('%')
        res.append(item)

    return ''.join(res)


def parse_qsl(qs):
    pairs = [s2 for s1 in qs.split('&') for s2 in s1.split(';')]
    res = []
    for name_value in pairs:
        try:
            name, value = name_value.split('=', 1)
        except ValueError:
            res.append((unquote(name_value), ''))
        else:
            res.append((unquote(name), unquote(value)))
    return res


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
    <p>
        <a href="/?power=on"><button class="button">ON</button></a>
        <a href="/?power=off"><button class="button button2">OFF</button></a>
    </p>
    <p>
        <a href="/?soft_reset"><button class="button">Soft reset Device</button></a>
        <a href="/?hard_reset"><button class="button">Hard reset Device</button></a>
    </p>
    <form action="/save" method="post">
        First name:<br>
        <input type="text" name="firstname" value="Mickey"><br>
        Last name:<br>
        <input type="text" name="lastname" value="Mouse+%E4%F6%FC%DF"><br><br>
        <input type="submit" value="Submit">
    </form> 
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
    if not ON_ESP:
        return

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
        if not ON_ESP:
            self.ip = "127.0.0.1"
        else:
            self.ip = get_wifi_ip()
            if self.ip is None:
                print('ERROR: WiFi not connected!')
                print('Hint: boot.py / main.py should create WiFi connection!')
                raise RuntimeError('No WiFi connection!')

        print('Start Webserver on: http;//%s:%i' % (self.ip, PORT))

        garbage_collection()

        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.s.bind((self.ip, PORT))
        self.s.listen(5)

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
        self.conn.send(b'HTTP/1.1 200 OK\n')
        self.conn.send(b'Content-Type: text/html\n')
        self.conn.send(b'Connection: close\n\n')

        if not ON_ESP:
            state="NOT ON ESP"
            utc=0,
            alloc=0
            free=0
        else:
            if relay_pin.value() == 1:
                state = 'ON'
            else:
                state = 'OFF'
            utc=rtc.datetime(),
            alloc=gc.mem_alloc()
            free=gc.mem_free()

        html = HTML.format(
            styles=STYLES,
            state=state,
            message=message,
            utc=utc,
            alloc=alloc,
            free=free,
        )
        self.conn.sendall(html.encode("UTF-8"))

    def send_redirect(self, url='/'):
        self.conn.send(b'HTTP/1.1 302 redirect\n')
        self.conn.send(b'Location: %s\n' % url)

    def handle_one_request(self):
        print('\nWait for connection on:', self.ip)

        if ON_ESP:
            led_pin.value(0)  # Turn LED on

        self.conn, addr = self.s.accept()

        if ON_ESP:
            led_pin.value(1)  # Turn LED off

        print('Connection from IP:', addr[0])

        request = self.conn.recv(2048)
        # print('request bytes:', request)

        request, body = request.split(b'\r\n\r\n',1)
        # print('request:', request)
        # print('body:', body)
        request, headers = request.split(b'\r\n',1)
        request = request.decode("UTF-8")
        # print('request: %r' % request)
        # print('headers:', headers)

        body = body.decode("UTF-8")
        print('body: %r' % body)

        try:
            method, url, version = request.split(' ', 2)
        except IndexError:
            print("Error parsing request: %r" % request)
            self.send_web_page(message='Error parsing request!')
        else:
            print('method: %r' % method)
            print('url: %r' % url)
            if method == 'POST':
                body = dict(parse_qsl(body))
                print('POST body:', body)

            if url == '/':
                print('response root page')
                self.send_web_page(message='')

            elif url == '/?power=on':
                if ON_ESP:
                    relay_pin.value(1)
                self.send_web_page(message='power on')

            elif url == '/?power=off':
                if ON_ESP:
                    relay_pin.value(0)
                self.send_web_page(message='power off')

            elif url == '/?soft_reset':
                if ON_ESP:
                    relay_pin.value(0)
                self.send_web_page(message='Soft reset device... Restart WebServer by pressing the Button on your device!')
                self.conn.close()
                print('Soft reset device...')
                self.running = False

            elif url == '/?hard_reset':
                if ON_ESP:
                    relay_pin.value(0)
                self.send_web_page(message='Hard reset device... Restart WebServer by pressing the Button on your device!')
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
        if ON_ESP:
            button_pin.irq(self.button_pressed)

        self.running = True
        while self.running:
            self.handle_one_request()

        sys.exit()


def main():
    web_switch = WebSwitch()
    web_switch.running = False
    web_switch.main_loop()


if __name__ == '__main__':
    main()


