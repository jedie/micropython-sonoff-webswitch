from http_utils import send_redirect
from pins import Pins


async def get_on(server, reader, writer, querystring):
    if server.watchdog.auto_timer.active:
        server.message = 'Deactivate automatic timer, first!'
    else:
        Pins.relay.on()
        server.message = 'power on'
    await send_redirect(writer)


async def get_off(server, reader, writer, querystring):
    if server.watchdog.auto_timer.active:
        server.message = 'Deactivate automatic timer, first!'
    else:
        Pins.relay.off()
        server.message = 'power off'
    await send_redirect(writer)
