import machine
from leds import Led
from micropython import const

_PIN_NO_POWER_LED = const(13)
_PIN_NO_RELAY = const(12)  # relay + red led
_PIN_NO_BUTTON = const(0)


class Pins:
    def __init__(self):
        self.power_led_pin = machine.Pin(_PIN_NO_POWER_LED, machine.Pin.OUT)
        self.power_led = Led(name='power', pin=self.power_led_pin, on=0, off=1)

        self.relay_pin = machine.Pin(_PIN_NO_RELAY, machine.Pin.OUT)
        self.relay = Led(name='relay', pin=self.relay_pin, on=1, off=0)

        self.button_pin = machine.Pin(_PIN_NO_BUTTON, machine.Pin.IN)




