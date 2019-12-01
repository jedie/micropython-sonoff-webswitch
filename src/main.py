print('main.py')  # noqa isort:skip

import gc

from button_handler import init_button_irq
from pins import Pins
from rtc import Rtc
from utils import ResetDevice
from wifi import WiFi

rtc = Rtc()
pins = Pins()

init_button_irq(rtc, pins)

wifi = WiFi(rtc=rtc, power_led=pins.power_led, verbose=True)
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

    watchdog = Watchdog(wifi=wifi, rtc=rtc)
    gc.collect()
    WebServer(pins=pins, rtc=rtc, watchdog=watchdog).run()
else:
    print('start OTA')
    pins.power_led.off()
    rtc.save(data={_RTC_KEY_RUN: _RUN_WEB_SERVER})
    from ota_client import OtaUpdate

    gc.collect()
    OtaUpdate().run()


ResetDevice(rtc=rtc, reason='unknown').reset()
