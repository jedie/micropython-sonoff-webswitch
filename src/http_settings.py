import gc
import sys

from template import render


async def get_wifi(server, reader, writer, querystring, body):
    from config_files import get_json_config
    wifi_configs = get_json_config(key='wifi')

    del get_json_config
    del sys.modules['config_files']
    gc.collect()

    settings = []
    for key, value in wifi_configs.items():
        settings.append(
            '%s: %s<br>' % (key, repr(value[0] + '*' * (len(value) - 2) + value[-1]))
        )

    await server.send_html_page(
        writer,
        filename='webswitch.html',
        content_iterator=render(
            filename='http_settings_wifi.html',
            context={
                'settings': ''.join(settings)
            },
            content_iterator=None
        ),
    )


async def get_set_timezone(server, reader, writer, querystring, body):
    from timezone import restore_timezone
    await server.send_html_page(
        writer,
        filename='webswitch.html',
        content_iterator=render(
            filename='http_settings_timezone.html',
            context={
                'offset': '%+i' % restore_timezone()
            },
            content_iterator=None
        ),
    )


async def post_set_timezone(server, reader, writer, querystring, body):
    from urllib_parse import request_query2dict
    body = request_query2dict(body)
    del request_query2dict
    del sys.modules['urllib_parse']
    gc.collect()

    offset = int(body['offset'])
    if not -12 <= offset <= 12:
        server.message = 'Offset is out of range!'
    else:
        from timezone import save_timezone
        save_timezone(offset_h=int(offset))
        del save_timezone
        del sys.modules['timezone']
        gc.collect()

        # Change the time to the right time zone
        from ntp import ntp_sync
        ntp_sync()
        del ntp_sync
        del sys.modules['ntp']
        gc.collect()

        server.message = 'Save timezone %+i' % offset

    from http_utils import send_redirect
    await send_redirect(writer, url='/settings/set_timezone/')
