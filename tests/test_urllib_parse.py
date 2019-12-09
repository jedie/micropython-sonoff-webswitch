
from unittest import TestCase

from urllib_parse import request_query2dict


class UrllibParseTestCase(TestCase):
    def test_request_query2dict(self):
        assert request_query2dict('timers=6%3A00-8%3A00+%0D%0A19%3A00-20%3A00&active=off') == {
            'timers': '6:00-8:00 \r\n19:00-20:00',
            'active': 'off'
        }
        assert request_query2dict('foo=%%&bar=%%%') == {'bar': '%%%', 'foo': '%%'}
        assert request_query2dict('foo=&bar=') == {'bar': '', 'foo': ''}
