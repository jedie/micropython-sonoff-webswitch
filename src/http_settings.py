
import sys


async def get_wifi(server, reader, writer, querystring, body):
    """
    Display existing WiFi settings with mask password
    """
    from config_files import get_json_config
    wifi_configs = get_json_config(key='wifi')

    del get_json_config
    del sys.modules['config_files']

    settings = []

    if wifi_configs is None:
        server.message = 'No WiFi settings saved!'
    else:
        for key, value in wifi_configs.items():
            settings.append(
                '%s: %s<br>' % (key, repr(value[0] + '*' * (len(value) - 2) + value[-1]))
            )

    from template import render
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


async def get_device_name_form(server, reader, writer, querystring, body, device_name=None):
    """
    send "set new device name" form
    """
    if not device_name:
        from device_name import get_device_name
        device_name = get_device_name()

    from template import render
    await server.send_html_page(
        writer,
        filename='webswitch.html',
        content_iterator=render(
            filename='http_settings_name.html',
            context={
                'device_name': device_name
            },
            content_iterator=None
        ),
    )


async def get_submit_device_name(server, reader, writer, querystring, body):
    """
    Save new device name
    """
    from urllib_parse import request_query2dict
    data = request_query2dict(querystring)
    del request_query2dict
    del sys.modules['urllib_parse']

    new_name = data.get('name', '')

    from device_name import save_device_name
    try:
        save_device_name(server, name=new_name)
    except ValueError as cleaned_name:
        await get_device_name_form(
            server, reader, writer, querystring, body, device_name=str(cleaned_name)
        )
    else:
        from http_utils import send_redirect
        await send_redirect(writer, url='/settings/device_name_form/')


async def get_timezone_form(server, reader, writer, querystring, body):
    """
    send "set timezone" form
    """
    from timezone import restore_timezone
    from template import render
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


async def get_submit_timezone(server, reader, writer, querystring, body):
    from urllib_parse import request_query2dict
    data = request_query2dict(querystring)
    del request_query2dict
    del sys.modules['urllib_parse']

    try:
        offset = int(data['offset'])
    except ValueError:
        server.message = 'Wrong offset: %r' % data.get('offset')
    else:
        if not -12 <= offset <= 12:
            server.message = 'Offset is out of range!'
        else:
            from timezone import save_timezone
            save_timezone(offset_h=int(offset))
            del save_timezone
            del sys.modules['timezone']

            # Change the time to the right time zone
            from ntp import ntp_sync
            ntp_sync(server.context)
            del ntp_sync
            del sys.modules['ntp']

            server.message = 'Save timezone %+i' % offset

    from http_utils import send_redirect
    await send_redirect(writer, url='/settings/timezone_form/')
