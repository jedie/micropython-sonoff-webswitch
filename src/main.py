print('main.py')

import time
time.sleep(1)

import sys
sys.modules.clear()

import gc
gc.collect()

from button_handler import Button
from pins import Pins
from rtc import Rtc
from wifi import WiFi


__version__ = 'v0.4.1'

rtc = Rtc()

# Init device button IRQ:
Pins.button_pin.irq(Button(rtc).irq_handler)

wifi = WiFi(rtc=rtc, power_led=Pins.power_led)
wifi.ensure_connection()
print('wifi: %s' % wifi)

_RTC_KEY_RUN = 'run'
_RUN_WEB_SERVER = 'web-server'


if rtc.d.get(_RTC_KEY_RUN) == _RUN_WEB_SERVER:
    print('start webserver')
    rtc.save(data={_RTC_KEY_RUN: None})  # run OTA client on next boot
    from webswitch import WebServer  # noqa isort:skip
    from watchdog import Watchdog  # noqa isort:skip
    from power_timer import AutomaticTimer  # noqa isort:skip

    gc.collect()
    WebServer(
        rtc=rtc,
        watchdog=Watchdog(wifi=wifi, rtc=rtc, auto_timer=AutomaticTimer(rtc=rtc)),
        version=__version__
    ).run()
else:
    print('start OTA')
    Pins.power_led.off()
    rtc.save(data={_RTC_KEY_RUN: _RUN_WEB_SERVER})  # run web server on next boot
    from ota_client import OtaUpdate

    gc.collect()
    OtaUpdate().run()


from reset import ResetDevice
ResetDevice(rtc=rtc, reason='unknown').reset()
