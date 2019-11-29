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
from rtc_memory import rtc_memory  # noqa isort:skip
from wifi import wifi  # noqa isort:skip

print('wifi:', wifi)
print('power_led:', power_led)
print('relay:', relay)


# from ota_client import do_ota_update
# print(do_ota_update())
# sys.exit()


def ota_on_startup():
    print('Check OTA on startup.')
    do_ota = False
    if rtc_memory.d.get('run') == 'ota-update':
        print('OTA is requested')  # e.g.: via web page
        del(rtc_memory.d['run'])
        do_ota = True

    if not do_ota and 'OTA-OK' not in rtc_memory.d:
        print('Do on OTA on startup')
        rtc_memory.save(data={'OTA-OK': 0})  # Only one at startup
        do_ota = True

    if not do_ota:
        return

    print('Run OTA Update on start')
    try:
        from ota_client import do_ota_update
        ok = do_ota_update()
        if ok == 'OK':
            rtc_memory.incr_rtc_count(key='OTA-OK')
    except Exception as e:
        rtc_memory.incr_rtc_count(key='OTA-ERROR')
        rtc_memory.save(data={'OTA last': str(e)})
    finally:
        print('Hard reset device after OTA update...')
        time.sleep(1)
        machine.reset()
        time.sleep(1)
        sys.exit()


power_led.off()
ota_on_startup()
power_led.on()
gc.collect()

from watchdog import watchdog  # noqa isort:skip
print('watchdog:', watchdog)

print('gc.collect()')
gc.collect()

# Start the Webserver:
from webswitch import main  # noqa isort:skip
main()
