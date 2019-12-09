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

    context = {
        'timers': timers,
        'on_selected': 'selected' if server.power_timer.active else '',
        'off_selected': '' if server.power_timer.active else 'selected',
    }

    from times_utils import get_active_days
    active_days = get_active_days()
    del get_active_days
    del sys.modules['times_utils']
    gc.collect()

    for day_no in range(7):
        context['d%i' % day_no] = 'checked' if day_no in active_days else ''

    from template import render
    await server.send_html_page(
        writer,
        filename='webswitch.html',
        content_iterator=render(
            filename='http_set_timer.html',
            context=context,
            content_iterator=None
        ),
    )


async def get_submit(server, reader, writer, querystring):
    from urllib_parse import request_query2dict
    get_parameters = request_query2dict(querystring)
    del request_query2dict
    del sys.modules['urllib_parse']
    gc.collect()

    from times_utils import parse_timers, save_timers, save_active_days
    try:
        timers = parse_timers(get_parameters['timers'])
        del parse_timers

        save_timers(timers)
        del save_timers

        power_timer_active = get_parameters['active'] == 'on'

        save_active_days(tuple(sorted([
            no for no in range(7)
            if 'd%i' % no in get_parameters
        ])))
        del save_active_days

        from rtc import update_rtc_dict
        update_rtc_dict(data={
            constants.POWER_TIMER_ACTIVE_KEY: power_timer_active,
        })
        del update_rtc_dict
    except ValueError as e:
        server.message = 'Timers error: %s' % e
        await get_form(server, reader, writer, querystring, timers=get_parameters['timers'])
        return

    del get_parameters
    del sys.modules['rtc']
    gc.collect()

    # Update power timer:
    if power_timer_active:
        server.message = 'Timers saved and activated.'
    else:
        server.message = 'Timers saved and deactivated.'

    # Force set 'active' and 'today_active' by schedule_next_switch() in update_power_timer():
    server.power_timer.active = None
    server.power_timer.today_active = None

    server.power_timer.schedule_next_switch()
    gc.collect()

    from http_utils import send_redirect
    await send_redirect(writer, url='/set_timer/form/')
