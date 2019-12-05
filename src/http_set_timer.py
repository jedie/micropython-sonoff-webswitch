import gc


async def get_form(server, reader, writer, querystring, timers=None):
    if timers is None:
        from times_utils import pformat_timers, restore_timers
        timers = pformat_timers(restore_timers())
        del pformat_timers
        del restore_timers

    gc.collect()
    from template import render

    await server.send_html_page(
        writer,
        filename='webswitch.html',
        content_iterator=render(
            filename='http_set_timer.html',
            context={
                'timers': timers,
                # 'on_value': get_timer_form_value(key='on'),
                # 'off_value': get_timer_form_value(key='off'),
                'on_selected': 'selected' if server.watchdog.auto_timer.active else '',
                'off_selected': '' if server.watchdog.auto_timer.active else 'selected',
            },
            content_iterator=None
        ),
    )


async def get_submit(server, reader, writer, querystring):
    from urllib_parse import querystring2dict
    get_parameters = querystring2dict(querystring)
    del querystring2dict

    from times_utils import parse_timers
    try:
        timers = parse_timers(get_parameters['timers'])
    except ValueError as e:
        server.message = 'Timers error: %s' % e
        await get_form(server, reader, writer, querystring, timers=get_parameters['timers'])
    else:
        from times_utils import save_timers
        save_timers(timers)
        del save_timers

        from rtc import update_rtc_dict
        update_rtc_dict(data={
            'active': get_parameters['active'] == 'on'
        })
        del update_rtc_dict

        server.message = 'Timers saved.'

        from http_utils import send_redirect
        await send_redirect(writer)
