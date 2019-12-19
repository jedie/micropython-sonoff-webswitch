import machine
from leds import PwmLed

if __name__ == '__main__':
    power_led = PwmLed(name='power', pin=machine.Pin(13, machine.Pin.OUT), on=0, off=1)

    for level in range(power_led.dim_max_level):
        print('\nset level to: %i' % level)
        power_led.set_dim_level(level)
        power_led.flash()

    power_led.off()
