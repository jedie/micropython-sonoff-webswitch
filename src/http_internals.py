import sys

import machine
import uos


async def get_show(server, reader, writer, querystring, body):
    from template import render
    from rtc import get_dict_from_rtc

    uname = uos.uname()

    template_context = {
        'rtc_memory': repr(get_dict_from_rtc()),

        'sysname': uname.sysname,
        'nodename': uname.nodename,
        'id': ':'.join(['%02x' % char for char in reversed(machine.unique_id())]),
        'machine': uname.machine,
        'release': uname.release,
        'mpy_version': uname.version,

        'sys_modules': ', '.join(sorted(sys.modules.keys())),
        'minimal_modules': ', '.join(server.context.minimal_modules)
    }

    for attr_name in dir(server.context):
        if attr_name.startswith('_'):
            continue
        value = str(getattr(server.context, attr_name))
        print(attr_name, value)

        template_context[attr_name] = value

    await server.send_html_page(
        writer,
        filename='webswitch.html',
        content_iterator=render(
            filename='http_internals.html',
            context=template_context,
            content_iterator=None
        ),
    )


async def get_clear(server, reader, writer, querystring, body):
    from http_utils import send_redirect
    from rtc import clear_rtc_dict
    clear_rtc_dict()
    server.message = 'RTC RAM cleared'
    await send_redirect(writer, url='/internals/show/')  # reload internal page


async def get_reset(server, reader, writer, querystring, body):
    from http_utils import send_redirect
    server.message = 'Reset device... Please reload the page in a few seconds.'

    await send_redirect(writer, url='/internals/show/')  # reload internal page

    from reset import ResetDevice
    ResetDevice(reason='Reset via web page').schedule(period=15000)
