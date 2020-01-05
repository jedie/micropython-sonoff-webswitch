import gc
import sys

from pins import Pins


async def get_form(server, reader, writer, querystring, body):
    from led_dim_level_cfg import restore_power_led_level

    from template import render
    await server.send_html_page(
        writer,
        filename='webswitch.html',
        content_iterator=render(
            filename='http_set_dim_level.html',
            context={
                'max': len(Pins.power_led.duty_values) - 1,
                'value': restore_power_led_level()
            },
            content_iterator=None
        ),
    )


async def get_submit(server, reader, writer, querystring, body):
    from urllib_parse import request_query2dict
    data = request_query2dict(querystring)
    del request_query2dict
    del sys.modules['urllib_parse']
    gc.collect()

    from led_dim_level_cfg import set_power_led_level

    level = int(data['level'])
    print('Set LED dim level to: %r' % level)
    if not 0 <= level <= len(Pins.power_led.duty_values):
        server.message = 'Level is out of range!'
    else:
        set_power_led_level(level)

        server.message = 'Save dim level: %i' % level

    from http_utils import send_redirect
    await send_redirect(writer, url='/set_dim_level/form/')
