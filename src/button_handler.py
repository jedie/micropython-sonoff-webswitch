import gc

import utime as time
from pins import Pins


class Button:
    down_start = None

    def __init__(self, rtc):
        self.rtc = rtc

    def get_debounced_value(self, pin):
        """
        get debounced value by waiting for stable value
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

    def irq_handler(self, pin):
        gc.collect()
        Pins.power_led.off()
        button_value = self.get_debounced_value(pin)
        gc.collect()
        print('button_value:', button_value)
        if button_value == 0:
            # button pressed
            self.down_start = time.ticks_ms()

        elif button_value == 1:
            # button released
            Pins.power_led.on()

            duration_ms = time.ticks_diff(time.ticks_ms(), self.down_start)
            print('duration_ms:', duration_ms)
            if duration_ms > 2000:
                from reset import ResetDevice
                ResetDevice(self.rtc, 'After button long press')

            print('old state:', Pins.relay)
            Pins.relay.toggle()
            print('new state:', Pins.relay)

        gc.collect()
