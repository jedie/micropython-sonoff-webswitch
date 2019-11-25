import gc

import micropython

micropython.alloc_emergency_exception_buf(128)

# init own stuff:

from watchdog import watchdog  # noqa isort:skip
from wifi import wifi  # noqa isort:skip
from ntp import ntp_sync  # noqa isort:skip
from leds import power_led, relay  # noqa isort:skip
import button_handler  # noqa isort:skip

print('watchdog:', watchdog)
print('wifi:', wifi)
print('ntp_sync:', ntp_sync)
print('power_led:', power_led)
print('relay:', relay)

print('main.py wait with power led flash...')
power_led.flash(sleep=0.1, count=20)

print('gc.collect()')
gc.collect()


# Start the Webserver:
from webswitch import main  # noqa isort:skip
main()
