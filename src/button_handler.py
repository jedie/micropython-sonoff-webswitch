import gc
import sys

import machine
import micropython
import utime as time
from leds import power_led, relay
from pins import button_pin
from rtc_memory import RtcMemory


def reset_device():
    print('reset device...')
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
    gc.collect()
    RtcMemory().save(data={'run': 'ota-update'})  # Save to RTC RAM for next boot
    reset_device()


def _start_webserver():
    print('Start Webserver...')
    gc.collect()
    try:
        from webswitch import main  # noqa isort:skip
        main()
    except Exception as e:
        sys.print_exception(e)
        reset_device()


def start_webserver(_):
    print('Create timer to start Webserver...')
    gc.collect()
    timer = machine.Timer(-1)
    timer.init(
        mode=machine.Timer.ONE_SHOT,
        period=1000,
        callback=_start_webserver()
    )


class Button:
    down_start = None

    def irq_handler(self, pin):
        power_led.off()
        button_value = get_debounced_value(pin)

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
                print('reset')
                power_led.flash(sleep=0.1, count=20)
                machine.reset()
                time.sleep(1)
                sys.exit()
            elif duration_ms > 2000:
                print('Schedule OTA Updates after long press...')
                micropython.schedule(ota_update, None)
                power_led.flash(sleep=0.1, count=20)
            else:
                print('Schedule start webserver after button press...')
                micropython.schedule(start_webserver, None)

            print('old state:', relay)
            relay.toggle()
            print('new state:', relay)

        gc.collect()


button_pin.irq(Button().irq_handler)
