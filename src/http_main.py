import gc

from http_utils import send_redirect
from pins import Pins
from template import render


async def get_menu(server, reader, writer, querystring, body):
    await server.send_html_page(
        writer,
        filename='webswitch.html',
        content_iterator=render(
            filename='http_main_menu.html',
            context={},
            content_iterator=None
        ),
    )


async def get_on(server, reader, writer, querystring, body):
    Pins.relay.on()
    server.message = 'power on'
    server.power_timer.schedule_next_switch()
    gc.collect()
    await send_redirect(writer)


async def get_off(server, reader, writer, querystring, body):
    Pins.relay.off()
    server.message = 'power off'
    server.power_timer.schedule_next_switch()
    gc.collect()
    await send_redirect(writer)
