import pins
import utime as time


class Led:
    def __init__(self, name, pin, on, off):
        self.name = name
        self.pin = pin
        self._on = on
        self._off = off

    def on(self):
        self.pin.value(self._on)

    def off(self):
        self.pin.value(self._off)

    def toggle(self):
        self.pin.value(self._off if self.pin.value() else self._on)

    def flash(self, sleep=0.01, count=5):
        self._flash(sleep, count)

    def _flash(self, sleep, count):
        old_value = self.pin.value()
        for no in range(count):
            self.toggle()
            time.sleep(sleep)
        self.pin.value(old_value)

    @property
    def state(self):
        if self._on:
            return 'ON' if self.pin.value() else 'OFF'
        else:
            return 'OFF' if self.pin.value() else 'ON'

    def __str__(self):
        return '%s %s: %s' % (self.name, self.pin, self.state)


power_led = Led(name='power', pin=pins.power_led_pin, on=0, off=1)
relay = Led(name='relay', pin=pins.relay_pin, on=1, off=0)


if __name__ == '__main__':
    print(relay)
    print(power_led)