
import constants
import utime
from pins import Pins


def get_debounced_value(pin):
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
        utime.sleep_ms(1)
    return cur_value


class Button:
    down_start = None

    def irq_handler(self, pin):

        Pins.power_led.off()
        button_value = get_debounced_value(pin)

        print('button_value:', button_value)
        if button_value == 0:
            # button pressed
            self.down_start = utime.ticks_ms()

        elif button_value == 1:
            # button released
            Pins.power_led.on()

            duration_ms = utime.ticks_diff(utime.ticks_ms(), self.down_start)
            print('duration_ms:', duration_ms)
            if duration_ms > 2000:
                from reset import ResetDevice
                ResetDevice('After button long press').reset()
            else:
                print('Overwrite via button press')
                if Pins.relay.is_on:
                    Pins.relay.off()
                    overwrite_type = False
                else:
                    Pins.relay.on()
                    overwrite_type = True

                from rtc import update_rtc_dict
                update_rtc_dict({
                    constants.RTC_KEY_MANUAL_OVERWRITE: utime.time(),
                    constants.RTC_KEY_MANUAL_OVERWRITE_TYPE: overwrite_type
                })
