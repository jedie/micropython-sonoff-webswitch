import gc

import machine
import micropython
import utime as time

micropython.alloc_emergency_exception_buf(128)

for no in range(3, 0, -1):
    print('%i main.py wait...' % no)
    time.sleep(1)

from watchdog import watchdog  # noqa isort:skip
from wifi import wifi  # noqa isort:skip
from ntp import ntp_sync  # noqa isort:skip
from leds import power_led  # noqa isort:skip
import button_handler  # noqa isort:skip

print('watchdog:', watchdog)
print('wifi:', wifi)
print('ntp_sync:', ntp_sync)
print('power_led:', power_led)



print('gc.collect()')
gc.collect()


from webswitch import main  # noqa isort:skip
main()
