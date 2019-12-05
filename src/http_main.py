

from template import render


async def get_menu(server, reader, writer, url):
    await server.send_html_page(
        writer,
        filename='webswitch.html',
        content_iterator=render(
            filename='http_main_menu.html',
            context={
                'timers': 'TODO'
            },
            content_iterator=None
        ),
    )
