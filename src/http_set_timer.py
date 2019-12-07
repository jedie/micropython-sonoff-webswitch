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
    from power_timer_schedule import get_active_days
    active_days = get_active_days()
    del get_active_days
    del sys.modules['power_timer_schedule']
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

        from rtc import update_rtc_dict
        update_rtc_dict(data={
            constants.POWER_TIMER_ACTIVE_KEY: power_timer_active,
            constants.POWER_TIMER_WEEKDAYS_KEY: [
                no for no in range(7)
                if 'd%i' % no in get_parameters
            ]
        })
        del update_rtc_dict
    except ValueError as e:
        server.message = 'Timers error: %s' % e
        await get_form(server, reader, writer, querystring, timers=get_parameters['timers'])
        return

    del get_parameters
    del sys.modules['rtc']
    gc.collect()

    server.message = 'Timers saved.'

    # Update power timer:
    if power_timer_active:
        server.power_timer.active = True
    else:
        server.power_timer.active = False

    # Force set 'today_active' by schedule_next_switch() in update_power_timer():
    server.power_timer.today_active = None

    server.power_timer.schedule_next_switch()

    del sys.modules['times_utils']  # used in schedule_next_switch
    gc.collect()

    from http_utils import send_redirect
    await send_redirect(writer, url='/set_timer/form/')
