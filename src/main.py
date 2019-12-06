

import gc
import sys
import time

from button_handler import Button
from pins import Pins
from reset import ResetDevice
from rtc import get_rtc_value, update_rtc_dict
from wifi import WiFi

print('main.py')

time.sleep(1)

sys.modules.clear()

gc.collect()


__version__ = 'v0.5.0'


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
    from power_timer import PowerTimer  # noqa isort:skip

    power_timer = PowerTimer()
    power_timer.schedule_next_switch()

    gc.collect()
    WebServer(
        power_timer=power_timer,
        watchdog=Watchdog(
            wifi=wifi,
            check_callback=power_timer.schedule_next_switch
        ),
        version=__version__
    ).run()
else:
    print('start OTA')
    Pins.power_led.off()
    update_rtc_dict(data={_RTC_KEY_RUN: _RUN_WEB_SERVER})  # run web server on next boot
    from ota_client import OtaUpdate

    gc.collect()
    OtaUpdate().run()

ResetDevice(reason='unknown').reset()
