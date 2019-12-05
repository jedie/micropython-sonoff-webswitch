
from power_timer import get_timer_form_value
from template import render


async def get_menu(server, reader, writer, url):
    await server.send_html_page(
        writer,
        filename='webswitch.html',
        content_iterator=render(
            filename='http_main_menu.html',
            context={
                'on_value': get_timer_form_value(key='on'),
                'off_value': get_timer_form_value(key='off'),
                'on_selected': 'selected' if server.watchdog.auto_timer.active else '',
                'off_selected': '' if server.watchdog.auto_timer.active else 'selected',
            },
            content_iterator=None
        ),
    )
