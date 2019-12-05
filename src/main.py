print('main.py')

import time
time.sleep(1)

import sys
sys.modules.clear()

import gc
gc.collect()

from button_handler import Button
from pins import Pins

from rtc import get_rtc_value, update_rtc_dict
from wifi import WiFi


__version__ = 'v0.4.2'


# Init device button IRQ:
Pins.button_pin.irq(Button().irq_handler)

wifi = WiFi()
wifi.ensure_connection()
print('wifi: %s' % wifi)

_RTC_KEY_RUN = 'run'
_RUN_WEB_SERVER = 'web-server'


if get_rtc_value(_RTC_KEY_RUN) == _RUN_WEB_SERVER:
    print('start webserver')
    update_rtc_dict(data={_RTC_KEY_RUN: None})  # run OTA client on next boot
    from webswitch import WebServer  # noqa isort:skip
    from watchdog import Watchdog  # noqa isort:skip

    gc.collect()
    WebServer(
        watchdog=Watchdog(wifi=wifi),
        version=__version__
    ).run()
else:
    print('start OTA')
    Pins.power_led.off()
    update_rtc_dict(data={_RTC_KEY_RUN: _RUN_WEB_SERVER})  # run web server on next boot
    from ota_client import OtaUpdate

    gc.collect()
    OtaUpdate().run()

from reset import ResetDevice
ResetDevice(reason='unknown').reset()
