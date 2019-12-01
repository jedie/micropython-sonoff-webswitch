import gc
import sys

import constants
import machine
import micropython
import utime as time
from leds import power_led, relay
from pins import button_pin
from rtc_memory import rtc_memory


def reset_device(reason):
    print('Reset reason: %s' % reason)

    # Save reason in RTC RAM:
    rtc_memory.save(data={constants.RTC_KEY_RESET_REASON: reason})
    time.sleep(1)
    machine.reset()
    time.sleep(1)
    sys.exit()


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


def ota_update(_):
    print('Set OTA update RTC RAM trigger...')
    rtc_memory.save(data={'run': 'ota-update'})  # Save to RTC RAM for next boot
    reset_device('Schedule OTA Update')


def _start_webserver():
    print('Start Webserver...')
    try:
        from webswitch import main  # noqa isort:skip
        main()
    except Exception as e:
        sys.print_exception(e)
        reset_device('Restart web server error: %s' % e)


def start_webserver(_):
    print('Create timer to start Webserver...')
    timer = machine.Timer(-1)
    timer.init(
        mode=machine.Timer.ONE_SHOT,
        period=1000,
        callback=_start_webserver()
    )


class Button:
    down_start = None

    def irq_handler(self, pin):
        gc.collect()
        power_led.off()
        button_value = get_debounced_value(pin)
        gc.collect()
        print('button_value:', button_value)
        if button_value == 0:
            # button pressed
            self.down_start = time.ticks_ms()

        elif button_value == 1:
            # button released
            power_led.on()

            duration_ms = time.ticks_diff(time.ticks_ms(), self.down_start)
            print('duration_ms:', duration_ms)
            if duration_ms > 4000:
                reset_device('After button long press')
            elif duration_ms > 2000:
                print('Schedule OTA Updates after long press...')
                micropython.schedule(ota_update, None)
                power_led.flash(sleep=0.3, count=10)
            else:
                print('Schedule start webserver after button press...')
                micropython.schedule(start_webserver, None)

            print('old state:', relay)
            relay.toggle()
            print('new state:', relay)

        gc.collect()


def init_button_irq():
    button_pin.irq(Button().irq_handler)
