import gc

import micropython

print('main.py')
micropython.mem_info()

# init own stuff:

from leds import power_led  # noqa isort:skip
from button_handler import init_button_irq  # noqa isort:skip
from rtc_memory import rtc_memory  # noqa isort:skip
from wifi import WiFi  # noqa isort:skip

init_button_irq()

power_led.off()
wifi = WiFi(verbose=True)
wifi.ensure_connection()

print('wifi: %s' % wifi)

_RTC_KEY_RUN = 'run'
_RUN_OTA_UPDATE = 'ota-update'
_RUN_WEB_SERVER = 'web-server'

if rtc_memory.d.get(_RTC_KEY_RUN) == _RUN_WEB_SERVER:
    rtc_memory.save(data={_RTC_KEY_RUN: _RUN_OTA_UPDATE})
    power_led.on()
    from webswitch import WebServer  # noqa isort:skip
    from watchdog import Watchdog  # noqa isort:skip

    watchdog = Watchdog(wifi=wifi)
    gc.collect()
    WebServer(watchdog).run()
else:
    power_led.off()
    rtc_memory.save(data={_RTC_KEY_RUN: _RUN_WEB_SERVER})
    from ota_client import OtaUpdate
    gc.collect()
    OtaUpdate().run()
