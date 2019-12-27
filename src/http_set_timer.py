import gc
import sys

import constants


async def get_form(server, reader, writer, querystring, body):
    from times_utils import restore_timers, pformat_timers, get_active_days
    timers = pformat_timers(restore_timers())
    active_days = get_active_days()
    del restore_timers
    del pformat_timers
    del get_active_days
    del sys.modules['times_utils']
    gc.collect()

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
    """
    Note: POST request doesn't work:
    https://forum.micropython.org/viewtopic.php?f=2&t=7432
    """
    from urllib_parse import request_query2dict
    data = request_query2dict(querystring)

    del request_query2dict
    gc.collect()

    import times_utils
    try:
        timers = tuple(times_utils.parse_timers(data['timers']))
        gc.collect()
    except ValueError as e:
        gc.collect()
        server.message = 'Timers error: %s' % e
    else:
        print('Save timers:', timers)
        # Save timers to flash:
        from config_files import save_py_config

        save_py_config(
            module_name=constants.TIMERS_PY_CFG_NAME,
            value=timers
        )
        save_py_config(
            module_name=constants.ACTIVE_DAYS_PY_CFG_NAME,
            value=tuple([no for no in range(7) if 'd%i' % no in data])
        )

        del save_py_config
        del sys.modules['config_files']
        gc.collect()

        power_timer_active = data.get('active') == 'on'

        data = None  # can be collected
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

        # Force set values by update_relay_switch() in update_power_timer():
        server.context.power_timer_active = None
        server.context.power_timer_today_active = None
    gc.collect()

    from http_utils import send_redirect
    await send_redirect(writer, url='/set_timer/form/')
