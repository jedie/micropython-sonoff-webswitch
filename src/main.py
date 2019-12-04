print('main.py')

import sys
sys.modules.clear()

import gc
gc.collect()

from button_handler import init_button_irq
from pins import Pins
from rtc import Rtc
from wifi import WiFi

__version__ = 'v0.3.1'

rtc = Rtc()
pins = Pins()

init_button_irq(rtc, pins)

wifi = WiFi(rtc=rtc, power_led=pins.power_led)
wifi.ensure_connection()

print('wifi: %s' % wifi)

_RTC_KEY_RUN = 'run'
_RUN_OTA_UPDATE = 'ota-update'
_RUN_WEB_SERVER = 'web-server'


if rtc.d.get(_RTC_KEY_RUN) == _RUN_WEB_SERVER:
    print('start webserver')
    rtc.save(data={_RTC_KEY_RUN: _RUN_OTA_UPDATE})
    from webswitch import WebServer  # noqa isort:skip
    from watchdog import Watchdog  # noqa isort:skip
    from power_timer import AutomaticTimer  # noqa isort:skip

    gc.collect()
    WebServer(
        pins=pins, rtc=rtc,
        watchdog=Watchdog(wifi=wifi, rtc=rtc),
        auto_timer=AutomaticTimer(rtc=rtc, pins=pins),
        version=__version__
    ).run()
else:
    print('start OTA')
    pins.power_led.off()
    rtc.save(data={_RTC_KEY_RUN: _RUN_WEB_SERVER})
    from ota_client import OtaUpdate

    gc.collect()
    OtaUpdate().run()

from reset import ResetDevice
ResetDevice(rtc=rtc, reason='unknown').reset()
