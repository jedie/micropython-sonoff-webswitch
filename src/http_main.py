from power_timer import get_timer_form_value


async def get_menu(server, reader, writer, url):
    await server.send_html_page(
        writer,
        filename='webswitch.html',
        context={
            'state': server.pins.relay.state,
            'on_value': get_timer_form_value(server.rtc, key='on'),
            'off_value': get_timer_form_value(server.rtc, key='off'),
            'on_selected': 'selected' if server.auto_timer.active else '',
            'off_selected': '' if server.auto_timer.active else 'selected',
        }
    )