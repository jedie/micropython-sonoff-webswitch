import time

for no in range(5, 1, -1):
    print('%i main.py wait...' % no)
    time.sleep(1)


print('gc.collect()')
import gc
gc.collect()


print('Imports')
import machine
try:
    import usocket as socket
except BaseException:
    import socket


led_pin = machine.Pin(13, machine.Pin.OUT, value=0)  # turn power LED on
relay_pin = machine.Pin(12, machine.Pin.OUT, value=0)  # turn replay off
button_pin = machine.Pin(0, machine.Pin.IN)


rtc = machine.RTC()


STYLES = """
body{font-family: Helvetica; display:inline-block; margin: 0px auto; text-align: center;}
h1{color: #0F3376; padding: 2vh;}
p{font-size: 1.5rem;}
.button{
  display: inline-block; background-color: #e7bd3b; border: none;
  border-radius: 4px; color: white; padding: 16px 40px; text-decoration: none; font-size: 30px; margin: 2px; cursor: pointer;
}
.button2{background-color: #4286f4;}
"""


HTML = """<html>
<head>
    <title>Sonoff S20 - ESP Web Server</title>
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <link rel="icon" href="data:,">
    <style>{styles}</style>
</head>
<body>
  <h1>Sonoff S20 - ESP Web Server</h1>
  <p>state: <strong>{state}</strong></p>
  <p><a href="/?power=on"><button class="button">ON</button></a></p>
  <p><a href="/?power=off"><button class="button button2">OFF</button></a></p>
  <p><a href="/?gc"><button class="button">Run a garbage collection</button></a></p>
  <p><small>
      {alloc}bytes of heap RAM that are allocated<br>
      {free}bytes of available heap RAM (-1 == amount is not known)<br>
      Server time in UTC: {utc}
  </small></p>
</body>
</html>
"""



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
        state = "ON"
    else:
        state = "OFF"

    return HTML.format(
        styles=STYLES,
        state=state,
        utc=rtc.datetime(),
        alloc=gc.mem_alloc(),
        free=gc.mem_free(),
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



print('init socket')
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind(('', 80))
s.listen(5)



def response_redirect(conn, url='/'):
    conn.send('HTTP/1.1 302 redirect\n')
    conn.send('Location: %s\n' % url)
    conn.send('Connection: close\n\n')
    conn.close()



while True:
    print('\nwait for connection...')

    led_pin.value(0)  # Turn LED on
    conn, addr = s.accept()
    led_pin.value(1)  # Turn LED off
    print('Connection from IP:', addr[0])

    header = conn.recv(1024)
    print('Header:', header)

    request = header.split(b'\r\n')[0].decode("ASCII")
    print('Request: %r' % request)

    url = request.split(' ', 2)[1]
    print('url: %r' % url)

    if url == '/':
        print('response root page')
        response = web_page()
        conn.send('HTTP/1.1 200 OK\n')
        conn.send('Content-Type: text/html\n')
        conn.send('Connection: close\n\n')
        conn.sendall(response)
        conn.close()

    elif url == '/?power=on':
        print('POWER ON')
        relay_pin.value(1)
        response_redirect(conn, url='/')

    elif url == '/?power=off':
        print('POWER OFF')
        relay_pin.value(0)
        response_redirect(conn, url='/')

    elif url == '/?gc':
        print('Run a garbage collection')
        alloced = gc.mem_alloc()
        gc.collect()
        print("Freeing: %i Bytes (now free: %i Bytes)" % (
            alloced - gc.mem_alloc(),
            gc.mem_free()
        ))
        response_redirect(conn, url='/')

    else:
        print("Error: unknown request!")
        conn.send('HTTP/1.1 404 not found\n')
        conn.send('Connection: close\n\n')
        conn.close()
        continue

    response = web_page()
    conn.send('HTTP/1.1 200 OK\n')
    conn.send('Content-Type: text/html\n')
    conn.send('Connection: close\n\n')
    conn.sendall(response)
    conn.close()

