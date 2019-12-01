import utime as time
from leds import power_led, relay


def test():
    print('test starts...')
    print('off')
    relay.off()
    print(relay)
    self.pins.power_led.off()
    print(power_led)

    time.sleep(1)

    print('on')
    self.pins.power_led.on()
    print(power_led)

    time.sleep(1)

    print('toggle 1')
    self.pins.power_led.toggle()

    time.sleep(1)

    print('toggle 2')
    self.pins.power_led.toggle()

    time.sleep(1)

    print('flash')
    self.pins.power_led.flash(sleep=0.1, count=20)

    relay.on()
    print(relay)

    print('test ends.')


if __name__ == '__main__':
    print('LED test start...')
    test()
    print('LED test end')
