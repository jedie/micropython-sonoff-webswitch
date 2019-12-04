import sys

import machine
import uos as os
from http_utils import send_redirect
from rtc import get_dict_from_rtc


async def get_show(server, reader, writer, url):
    uname = os.uname()
    await server.send_html_page(
        writer,
        filename='sys_internals.html',
        context={
            'watchdog': server.watchdog,
            'auto_timer': server.watchdog.auto_timer,
            'rtc_memory': repr(get_dict_from_rtc()),

            'nodename': uname.nodename,
            'id': ':'.join(['%02x' % char for char in reversed(machine.unique_id())]),
            'machine': uname.machine,
            'release': uname.release,
            'mpy_version': uname.version,

            'sys_modules': ', '.join(sys.modules.keys())
        }
    )


async def get_clear(server, reader, writer, get_parameters):
    server.rtc.clear()
    server.message = 'RTC RAM cleared'
    await send_redirect(writer)


async def get_reset(server, reader, writer, get_parameters):
    server.message = (
        'Reset device...'
        ' Restart WebServer by pressing the Button on your device!'
    )
    from reset import ResetDevice
    ResetDevice(reason='Reset via web page').schedule(period=5000)
    await send_redirect(writer)
