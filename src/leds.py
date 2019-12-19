import machine
import utime


class Led:
    def __init__(self, name, pin, on, off):
        self.name = name
        self.pin = pin
        self._on = on
        self._off = off
        self.is_on = None
        self.off()

    def on(self):
        self.pin.value(self._on)
        self.is_on = True

    def off(self):
        self.pin.value(self._off)
        self.is_on = False

    def toggle(self):
        if self.is_on:
            self.off()
        else:
            self.on()

    def flash(self, sleep=0.5, count=6):
        was_on = self.is_on
        for no in range(count):
            self.toggle()
            utime.sleep(sleep)
        if was_on:
            self.on()
        else:
            self.off()

    @property
    def state(self):
        return 'ON' if self.is_on else 'OFF'

    def __str__(self):
        return '%s %s: %s' % (self.name, self.pin, self.state)


class PwmLed(Led):
    def __init__(self, *args, **kwargs):
        self.duty_values = (None, 700, 900, 1000)
        self.duty = None  # Full ON as default

        super().__init__(*args, **kwargs)

        self.pwm = machine.PWM(self.pin, freq=100, duty=0)

    def set_dim_level(self, dim_level):
        assert 0 <= dim_level <= len(self.duty_values), 'level %r is not between 0 and %i' % (
            dim_level, len(self.duty_values)
        )

        was_on = self.is_on
        self.duty = self.duty_values[dim_level]
        if self.duty is None:
            self.off()
            self.deinit_pwm()
        if was_on:
            self.on()

    def on(self):
        if self.duty is not None:
            self.is_on = True
            self.pwm.duty(self.duty)
        else:
            super().on()

    def off(self):
        super().off()
        if self.duty is not None:
            self.deinit_pwm()

    def deinit_pwm(self):
        self.pwm.duty(0)
        self.pwm.freq(100)
        self.pwm.deinit()
