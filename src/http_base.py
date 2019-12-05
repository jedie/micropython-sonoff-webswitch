from http_utils import send_redirect
from pins import Pins
from power_timer import set_timer_from_web


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


async def get_set_timer(server, reader, writer, get_parameters):
    set_timer_from_web(get_parameters)
    server.message = 'Timer set'
    await send_redirect(writer)
