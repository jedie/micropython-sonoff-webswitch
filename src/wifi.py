
import sys

import network
import utime
from pins import Pins


def ensure_connection(context):
    """
    will be called from:
        - main.py
        - watchdog_checks.check()

    Must return True if connected to WiFi.
    """
    station = network.WLAN(network.STA_IF)  # WiFi station interface
    if not station.active():
        station.active(True)

    context.wifi_last_update = utime.time()

    if station.isconnected():
        print('Still connected:', station.ifconfig())
        context.wifi_connected += 1
        return True

    context.wifi_not_connected += 1
    Pins.power_led.off()

    from wifi_connect import connect
    connected_time = connect(station)

    del connect
    del sys.modules['wifi_connect']

    if context.wifi_first_connect_time is None:
        context.wifi_first_connect_time = connected_time

    return True


def init(context):
    print('Setup WiFi interfaces')

    Pins.power_led.off()

    access_point = network.WLAN(network.AP_IF)  # access-point interface
    if access_point.active():
        print('deactivate access-point interface...')
        access_point.active(False)

    return ensure_connection(context)
