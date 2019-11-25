import gc
import sys

import machine
import utime as time
from leds import power_led, relay
from pins import button_pin


def get_debounced_value(pin):
    """
    get debounced value from pin by waiting for stable value
    """
    cur_value = pin.value()
    stable = 0
    while stable < 40:
        if pin.value() == cur_value:
            stable += 1
        else:
            stable = 0
            cur_value = pin.value()
        time.sleep_ms(1)
    return cur_value


class Button:
    down_start = None

    def irq_handler(self, pin):
        power_led.off()
        button_value = get_debounced_value(pin)
        power_led.on()

        print('button_value:', button_value)
        if button_value == 0:
            # button pressed
            self.down_start = time.ticks_ms()
        elif button_value == 1:
            # button released
            duration_ms = time.ticks_diff(time.ticks_ms(), self.down_start)
            print('duration_ms:', duration_ms)
            if duration_ms > 2000:
                print('reset after long press...')
                power_led.flash(sleep=0.1, count=20)
                machine.reset()
                sys.exit()

            print('old state:', relay)
            relay.toggle()
            print('new state:', relay)

        gc.collect()


button_pin.irq(Button().irq_handler)
