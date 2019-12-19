import machine
from leds import Led, PwmLed
from micropython import const

_PIN_NO_POWER_LED = const(13)
_PIN_NO_RELAY = const(12)  # relay + red led
_PIN_NO_BUTTON = const(0)


class Pins:
    power_led_pin = machine.Pin(_PIN_NO_POWER_LED, machine.Pin.OUT)
    power_led = PwmLed(name='power', pin=power_led_pin, on=0, off=1)

    relay_pin = machine.Pin(_PIN_NO_RELAY, machine.Pin.OUT)
    relay = Led(name='relay', pin=relay_pin, on=1, off=0)

    button_pin = machine.Pin(_PIN_NO_BUTTON, machine.Pin.IN)
