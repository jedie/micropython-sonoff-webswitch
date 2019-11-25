import machine

power_led_pin = machine.Pin(13, machine.Pin.OUT)
relay_pin = machine.Pin(12, machine.Pin.OUT)  # relay + red led
button_pin = machine.Pin(0, machine.Pin.IN)