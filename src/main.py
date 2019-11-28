import gc
import sys

import machine
import micropython
import utime as time

print('main.py')


micropython.mem_info()

# init own stuff:

from leds import power_led, relay  # noqa isort:skip
import button_handler  # noqa isort:skip
from rtc_memory import RtcMemory  # noqa isort:skip

print('power_led:', power_led)
print('relay:', relay)

if RtcMemory().rtc_memory.get('run') == 'ota-update':
    print('Run OTA Update on start')
    try:
        from ota_client import do_ota_update
        ok = do_ota_update()
        if ok == 'OK':
            RtcMemory().save(data={'run': None})
    except Exception as e:
        sys.print_exception(e)
    finally:
        print('Hard reset device after OTA update...')
        power_led.flash(sleep=0.4, count=20)
        time.sleep(1)
        machine.reset()
        time.sleep(1)
        sys.exit()
else:
    print('No OTA Update scheduled, ok')

gc.collect()

from watchdog import watchdog  # noqa isort:skip
from wifi import wifi  # noqa isort:skip


print('watchdog:', watchdog)
print('wifi:', wifi)

#print('main.py wait with power led flash...')
#power_led.flash(sleep=0.5, count=10)

print('gc.collect()')
gc.collect()

# Start the Webserver:
from webswitch import main  # noqa isort:skip
main()
