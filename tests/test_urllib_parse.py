
from unittest import TestCase

from urllib_parse import querystring2dict


class UrllibParseTestCase(TestCase):
    def test_querystring2dict(self):
        assert querystring2dict('timers=6%3A00-8%3A00+%0D%0A19%3A00-20%3A00&active=off') == {
            'timers': '6:00-8:00 \r\n19:00-20:00',
            'active': 'off'
        }
        assert querystring2dict('foo=%%&bar=%%%') == {'bar': '%%%', 'foo': '%%'}
        assert querystring2dict('foo=&bar=') == {'bar': '', 'foo': ''}
