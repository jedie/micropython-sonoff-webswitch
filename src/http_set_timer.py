from http_utils import send_redirect
from power_timer import set_timer_from_web


async def get_submit(server, reader, writer, get_parameters):
    set_timer_from_web(get_parameters)
    server.message = 'Timer data saved.'
    await send_redirect(writer)
