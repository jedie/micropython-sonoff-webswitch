import gc


async def get_menu(server, reader, writer, querystring, body):
    from template import render
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
    from pins import Pins
    Pins.relay.on()
    server.message = 'power on'
    server.power_timer.schedule_next_switch()
    gc.collect()
    from http_utils import send_redirect
    await send_redirect(writer)


async def get_off(server, reader, writer, querystring, body):
    from pins import Pins
    Pins.relay.off()
    server.message = 'power off'
    server.power_timer.schedule_next_switch()
    gc.collect()
    from http_utils import send_redirect
    await send_redirect(writer)
