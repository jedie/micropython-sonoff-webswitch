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
        if self.is_on:
            self.off()
        else:
            self.on()

    def flash(self, sleep=0.1, count=5):
        old_value = self.pin.value()
        for no in range(count):
            self.toggle()
            time.sleep(sleep)
        self.pin.value(old_value)

    @property
    def is_on(self):
        return self.pin.value() == self._on

    @property
    def state(self):
        return 'ON' if self.is_on else 'OFF'

    def __str__(self):
        return '%s %s: %s' % (self.name, self.pin, self.state)


if __name__ == '__main__':
    import machine
    relay = Led(name='relay', pin=machine.Pin(12, machine.Pin.OUT), on=1, off=0)
    relay.off()
    print(relay)
    relay.on()
    print(relay)
