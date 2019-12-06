from http_utils import send_redirect
from pins import Pins


async def get_on(server, reader, writer, querystring):
    Pins.relay.on()
    server.message = 'power on'
    await send_redirect(writer)


async def get_off(server, reader, writer, querystring):
    Pins.relay.off()
    server.message = 'power off'
    await send_redirect(writer)
