import gc
import sys

import constants


async def get_form(server, reader, writer, querystring, body):
    import times_utils
    timers = times_utils.pformat_timers(server.context.power_timer_timers)

    active_days = times_utils.get_active_days()

    # We need more free RAM to continue :-/
    server.context.watchdog.garbage_collection()

    # Maybe the timers was edited just before: Update the context with current informations:
    from power_timer import update_power_timer
    update_power_timer(server.context)

    # We need more free RAM to continue :-/
    server.context.watchdog.garbage_collection()

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


async def post_submit(server, reader, writer, querystring, body):
    from urllib_parse import request_query2dict
    body = request_query2dict(body)

    del request_query2dict
    del sys.modules['urllib_parse']
    gc.collect()

    import times_utils
    try:
        timers = tuple(times_utils.parse_timers(body['timers']))
    except ValueError as e:
        server.message = 'Timers error: %s' % e
    else:
        # Save timers to flash:
        times_utils.save_timers(timers)

        # Update context with current timers:
        server.context.power_timer_timers = timers

        power_timer_active = body.get('active') == 'on'

        times_utils.save_active_days(tuple(sorted([
            no for no in range(7)
            if 'd%i' % no in body
        ])))

        del sys.modules['times_utils']
        gc.collect()

        from rtc import update_rtc_dict
        update_rtc_dict(data={
            constants.POWER_TIMER_ACTIVE_KEY: power_timer_active,
            #
            # Deactivate manual overwrite, so that timers are used:
            constants.RTC_KEY_MANUAL_OVERWRITE_TYPE: None,
        })

        del update_rtc_dict
        del sys.modules['rtc']
        gc.collect()

        # Update power timer:
        if power_timer_active:
            server.message = 'Timers saved and activated.'
        else:
            server.message = 'Timers saved and deactivated.'

        # Force set 'active' and 'today_active' by update_relay_switch() in update_power_timer():
        server.context.power_timer_active = None
        server.context.power_timer_today_active = None

    gc.collect()

    from http_utils import send_redirect
    await send_redirect(writer, url='/set_timer/form/')
