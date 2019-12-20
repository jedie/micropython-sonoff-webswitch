

import constants


async def get_form(server, reader, writer, querystring, timers=None):
    if timers is None:
        from times_utils import pformat_timers, restore_timers
        timers = pformat_timers(restore_timers())

    from times_utils import get_active_days
    active_days = get_active_days()

    context = {
        'timers': timers,
        'on_selected': 'selected' if server.context.power_timer_active else '',
        'off_selected': '' if server.context.power_timer_active else 'selected',
    }
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


async def get_submit(server, reader, writer, querystring, body):
    from urllib_parse import request_query2dict
    get_parameters = request_query2dict(querystring)

    from times_utils import parse_timers, save_timers, save_active_days
    try:
        timers = tuple(parse_timers(get_parameters['timers']))
    except ValueError as e:
        server.message = 'Timers error: %s' % e
        await get_form(server, reader, writer, querystring, timers=get_parameters['timers'])
        return

    save_timers(timers)

    power_timer_active = get_parameters['active'] == 'on'

    save_active_days(tuple(sorted([
        no for no in range(7)
        if 'd%i' % no in get_parameters
    ])))

    # We need more free RAM to continue :-/
    server.context.watchdog.garbage_collection()

    from rtc import update_rtc_dict
    update_rtc_dict(data={
        constants.POWER_TIMER_ACTIVE_KEY: power_timer_active,
        #
        # Deactivate manual overwrite, so that timers are used:
        constants.RTC_KEY_MANUAL_OVERWRITE_TYPE: None,
    })

    # Update power timer:
    if power_timer_active:
        server.message = 'Timers saved and activated.'
    else:
        server.message = 'Timers saved and deactivated.'

    # Force set 'active' and 'today_active' by update_relay_switch() in update_power_timer():
    server.context.power_timer_active = None
    server.context.power_timer_today_active = None

    # from power_timer import update_power_timer
    # update_power_timer(server.context)

    from http_utils import send_redirect
    await send_redirect(writer, url='/set_timer/form/')
