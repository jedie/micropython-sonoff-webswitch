import gc
import sys

import network
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

    if station.isconnected():
        print('Still connected:', station.ifconfig())
        context.wifi_connected += 1
        return True

    context.wifi_not_connected += 1
    Pins.power_led.off()

    from wifi_connect import connect
    connected_time = connect(context, station)

    del connect
    del sys.modules['wifi_connect']

    if context.wifi_first_connect_time is None:
        context.wifi_first_connect_time = connected_time

    return True


def init(context):
    print('Setup WiFi interfaces')

    Pins.power_led.off()

    from device_name import get_device_name
    context.device_name = get_device_name()

    del get_device_name
    del sys.modules['device_name']
    gc.collect()

    access_point = network.WLAN(network.AP_IF)  # access-point interface
    if access_point.active():
        print('deactivate access-point interface...')
        access_point.active(False)

    return ensure_connection(context)
