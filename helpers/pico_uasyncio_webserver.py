"""
    A very, very minimalistic uasyncio based micropython web server
"""

import network
import uasyncio
import utime


async def request_handler(reader, writer):
    print('-' * 100)
    peername = writer.get_extra_info('peername')
    method, url, http_version = (await reader.readline()).decode().strip().split()
    print(peername, method, url, http_version)

    while True:
        line = await reader.readline()
        if line == b'\r\n':  # header ends
            break
        print(line.decode().strip())

    await writer.awrite(b'HTTP/1.0 200 OK\r\n')
    await writer.awrite(b'Content-type: text/plain; charset=utf-8\r\n\r\n')

    await writer.awrite(b'Your IP: %s port:%s\n' % peername)
    await writer.awrite(b'Device time:%s\n' % utime.time())

    await writer.aclose()


if __name__ == '__main__':
    sta_if = network.WLAN(network.STA_IF)
    print('WiFi information:', sta_if.ifconfig())

    loop = uasyncio.get_event_loop()
    loop.create_task(uasyncio.start_server(request_handler, '0.0.0.0', 80))

    print('Web server started...')
    loop.run_forever()
