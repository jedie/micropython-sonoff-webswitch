import gc
import sys

import constants


async def get_form(server, reader, writer, querystring, timers=None):
    if timers is None:
        from times_utils import pformat_timers, restore_timers
        timers = pformat_timers(restore_timers())
        del pformat_timers
        del restore_timers
        del sys.modules['times_utils']

    gc.collect()
    from template import render

    await server.send_html_page(
        writer,
        filename='webswitch.html',
        content_iterator=render(
            filename='http_set_timer.html',
            context={
                'timers': timers,
                'on_selected': 'selected' if server.power_timer.active else '',
                'off_selected': '' if server.power_timer.active else 'selected',
            },
            content_iterator=None
        ),
    )


async def get_submit(server, reader, writer, querystring):
    from urllib_parse import querystring2dict
    get_parameters = querystring2dict(querystring)
    del querystring2dict
    del sys.modules['urllib_parse']
    gc.collect()

    from times_utils import parse_timers, save_timers
    try:
        timers = parse_timers(get_parameters['timers'])

        save_timers(timers)
        del save_timers

        power_timer_active = get_parameters['active'] == 'on'
        if power_timer_active:
            server.power_timer.active = True
        else:
            server.power_timer.active = False

        from rtc import update_rtc_dict
        update_rtc_dict(data={
            constants.POWER_TIMER_ACTIVE_KEY: power_timer_active
        })
        del update_rtc_dict
    except ValueError as e:
        server.message = 'Timers error: %s' % e
        await get_form(server, reader, writer, querystring, timers=get_parameters['timers'])

    del get_parameters
    del sys.modules['times_utils']
    del sys.modules['rtc']
    gc.collect()

    server.message = 'Timers saved.'
    server.power_timer.schedule_next_switch()

    from http_utils import send_redirect
    await send_redirect(writer, url='/set_timer/form/')
