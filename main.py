import time
import machine

try:
  import usocket as socket
except:
  import socket

led_pin = machine.Pin(13, machine.Pin.OUT, value=0) # turn power LED on
relay_pin = machine.Pin(12, machine.Pin.OUT, value=0) # turn replay off
button_pin = machine.Pin(0, machine.Pin.IN)

STYLES="""
html{text-align: center;}
body{font-family: Helvetica;}
h1{color: #0F3376;}
.button{
  background-color: #e7bd3b;
  border-radius: 12px; color: white; padding: 10px 40px; text-decoration: none; font-size: 30px; 
  cursor: pointer;
}
.button-off{background-color: #4286f4;}
"""

HTML="""<html>
<head>
    <title>Sonoff S20 Web Switch</title>
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <link rel="icon" href="data:,">
    <style>{styles}</style>
</head>
<body>
  <h1>Sonoff S20 Web Switch</h1> 
  <p>state: <strong>{state}</strong></p>
  <p><a href="/?power=on"><button class="button">ON</button></a></p>
  <p><a href="/?power=off"><button class="button button-off">OFF</button></a></p>
  <p><a href="https://github.com/jedie/micropython-sonoff-webswitch">github.com/jedie/micropython-sonoff-webswitch</a></p>
  <p><small>(Server time in UTC: {utc})</small></p>
</body>
</html>
"""

rtc = machine.RTC()


def get_value(pin):
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


def web_page():
    if relay_pin.value() == 1:
        state="ON"
    else:
        state="OFF"

    return HTML.format(
        styles=STYLES,
        state=state,
        utc=rtc.datetime()
    )


def button_pressed(pin):
    print('button pressed...')
    cur_button_value = get_value(pin)
    if cur_button_value == 1:
        if relay_pin.value() == 1:
            print('turn off by button.')
            relay_pin.value(0)
        else:
            print('turn on by button.')
            relay_pin.value(1)

button_pin.irq(button_pressed)


s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind(('', 80))
s.listen(5)

print("Start Webserver...")



while True:
    print('\nwait for connection...')
    
    led_pin.value(0) # Turn LED on
    conn, addr = s.accept()
    led_pin.value(1) # Turn LED off
    print('Connection from IP:', addr[0])

    header = conn.recv(1024)
    print('Header:', header)

    request=header.split(b'\r\n')[0].decode("ASCII")
    print('Request:', request)
    path=request.split(' ',2)[1]
    print('path:', path)

    if path == '/?power=on':
        print('POWER ON')
        relay_pin.value(1)
    elif path == '/?power=off':
        print('POWER OFF')
        relay_pin.value(0)
    elif 'favicon.ico' in path:
        print("favicon.ico -> 404")
        conn.send('HTTP/1.1 404 not found\n')
        conn.send('Connection: close\n\n')
        conn.close()
        continue
    elif '?' in path:
        print("Error: unknown request!")
        # redirect to "/":
        conn.send('HTTP/1.1 301 Moved Permanently\n')
        conn.send('Location: /\n')
        conn.send('Connection: close\n\n')
        conn.close()
        continue
    
    response = web_page()
    conn.send('HTTP/1.1 200 OK\n')
    conn.send('Content-Type: text/html\n')
    conn.send('Connection: close\n\n')
    conn.sendall(response)
    conn.close()
