import constants
import utime


async def get_menu(server, reader, writer, querystring, body):
    from template import render
    await server.send_html_page(
        writer,
        filename='webswitch.html',
        content_iterator=render(
            filename='http_main_menu.html',
            context={},
            content_iterator=None
        ),
    )


async def _switch(server, writer, turn_on):
    """
    We only save the 'manual overwrite' information to RTC RAM and set the 'message'.
    The update_relay_switch() will turn on/off the relay switch
    """
    server.message = 'power %s' % ('on' if turn_on else 'off')

    from rtc import update_rtc_dict
    update_rtc_dict({
        constants.RTC_KEY_MANUAL_OVERWRITE: utime.time(),
        constants.RTC_KEY_MANUAL_OVERWRITE_TYPE: turn_on
    })

    from power_timer import update_power_timer
    update_power_timer(context=server.context)

    from http_utils import send_redirect
    await send_redirect(writer)


async def get_on(server, reader, writer, querystring, body):
    """
    Manual overwrite and turn the power relay switch ON
    """
    await _switch(server, writer, turn_on=True)


async def get_off(server, reader, writer, querystring, body):
    """
    Manual overwrite and turn the power relay switch OFF
    """
    await _switch(server, writer, turn_on=False)
