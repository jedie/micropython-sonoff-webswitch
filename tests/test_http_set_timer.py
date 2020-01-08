from power_timer import active_today
from rtc import get_dict_from_rtc
from tests.base import WebServerTestCase
from times_utils import get_active_days, pformat_timers, restore_timers


class HttpMainMenuTestCase(WebServerTestCase):
    async def test_set_timer(self):

        # Set timer:

        response = await self.get_request(
            request_line=(
                b"GET"
                b" /set_timer/submit/"
                b"?timers=07%3A00+-+08%3A00%0D%0A20%3A00+-+22%3A35"
                b"&d0=on&d1=on&d2=on&d3=on&d4=on"  # only MO-FR, not SA+SU
                b"&active=on"
                b" HTTP/1.1"
            )
        )
        assert response == b'HTTP/1.0 303 Moved\r\nLocation: /set_timer/form/\r\n\r\n'
        assert self.web_server.message == 'Timers saved and activated.'

        timers = pformat_timers(restore_timers())
        assert timers == '07:00 - 08:00\n20:00 - 22:35'

        active_days = tuple(get_active_days())
        assert active_days == (0, 1, 2, 3, 4)  # only MO-FR, not SA+SU

        assert get_dict_from_rtc() == {'active': True, 'manual-type': None}

        assert active_today() is True

        # Request the form:

        response = await self.get_request(
            request_line=b"GET /set_timer/form/ HTTP/1.1"
        )
        self.assert_response_parts(
            response,
            parts=(
                'HTTP/1.0 200 OK',
                '<html>',
                '<title>network name-04030201 - OFF</title>',
                '<p>Power switch state: <strong>OFF</strong></p>',
                '<p><strong>Switch on in 6 h at 20:00 h.</strong></p>',
                '<p>Timers saved and activated.</p>',

                '<textarea name="timers" rows="6" cols="13">07:00 - 08:00',
                '20:00 - 22:35</textarea>',

                '<option value="on" selected>ON</option>',

                'RAM total: 1.95 KB, used: 0.98 KB, free: 0.98 KB<br>',
                'Server local time: 2019-05-01 13:12:11',
                '</html>'
            )
        )
        assert self.web_server.message == 'Timers saved and activated.'
