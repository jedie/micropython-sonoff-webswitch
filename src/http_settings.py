import gc
import sys

from template import render


async def get_wifi(server, reader, writer, url):
    from get_config import get_config
    config = get_config(key='wifi')

    del get_config
    del sys.modules['get_config']
    gc.collect()

    settings = []
    for key, value in config.items():
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
