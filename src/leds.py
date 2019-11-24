import gc

import machine
import utime as time


class Led:
    def __init__(self, no):
        self.pin = machine.Pin(no, machine.Pin.OUT)

    def on(self):
        """ turn LED on """
        self.pin.value(0)

    def off(self):
        """ turn LED off """
        self.pin.value(1)

    def toggle(self):
        self.pin.value(0 if self.pin.value() else 1)

    def flash(self, sleep=0.01, count=5):
        self._flash(sleep, count)

    def _flash(self, sleep, count):
        old_value = self.pin.value()
        for no in range(count):
            self.toggle()
            time.sleep(sleep)
        self.pin.value(old_value)


class PowerLed(Led):
    def __init__(self):
        super().__init__(no=13)


power_led = PowerLed()


def test():
    print('test starts...')
    print('off')
    power_led.off()
    time.sleep(1)
    print('on')
    power_led.on()
    time.sleep(1)
    print('toggle 1')
    power_led.toggle()
    time.sleep(1)
    print('toggle 2')
    power_led.toggle()
    time.sleep(1)

    print('flash')
    power_led.flash(sleep=0.1, count=5)

    gc.collect()
    print('test ends.')


if __name__ == '__main__':
    print('LED test start...')
    test()
    print('LED test end')
