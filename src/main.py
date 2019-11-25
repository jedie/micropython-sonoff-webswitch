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

print('watchdog:', watchdog)
print('wifi:', wifi)
print('ntp_sync:', ntp_sync)
print('power_led:', power_led)


def get_debounced_value(pin):
    """get debounced value from pin by waiting for 20 msec for stable value"""
    cur_value = pin.value()
    stable = 0
    while stable < 20:
        if pin.value() == cur_value:
            stable = stable + 1
        else:
            stable = 0
            cur_value = pin.value()
    time.sleep_ms(1)
    return cur_value


def button_pressed(pin):
    print('button pressed...')
    cur_button_value = get_debounced_value(pin)
    if cur_button_value == 1:
        if relay_pin.value() == 1:
            print('turn off by button.')
            relay_pin.value(0)
        else:
            print('turn on by button.')
            relay_pin.value(1)

        garbage_collection()


button_pin = machine.Pin(0, machine.Pin.IN)
button_pin.irq(button_pressed)


print('gc.collect()')
gc.collect()


from webswitch import main  # noqa isort:skip
main()
