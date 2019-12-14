import gc
import sys

import network
import utime
from pins import Pins


def get_known_ssid(station, wifi_configs, verbose):
    print('Scan WiFi...')

    known_ssid = None
    for no in range(3):
        for info in station.scan():
            Pins.power_led.toggle()
            ssid, bssid, channel, RSSI, auth_mode, hidden = info
            ssid = ssid.decode("UTF-8")
            if verbose:
                print(
                    'SSID: %s (channel: %s authmode: %s hidden: %s)' % (
                        ssid, channel, auth_mode, hidden
                    )
                )
            if ssid in wifi_configs:
                known_ssid = ssid
        if known_ssid is not None:
            return known_ssid

    print('ERROR: No known WiFi SSID found!')
    Pins.power_led.flash(sleep=0.2, count=20)


def connect2ssid(station, ssid, password, verbose):
    for no in range(0, 3):
        if verbose:
            print('PHY mode: %s' % network.phy_mode())
        # print('Connect to Wifi access point:', ssid, repr(password))
        if verbose:
            print('Connect to Wifi access point: %s' % ssid)
        Pins.power_led.toggle()
        station.connect(ssid, password)
        for wait_sec in range(30, 1, -1):
            status = station.status()
            if status == network.STAT_GOT_IP:
                Pins.power_led.on()
                return utime.time()
            elif status == network.STAT_WRONG_PASSWORD:
                print('Wrong password!')
                return
            if verbose:
                print('wait %i...' % wait_sec)
            Pins.power_led.flash(sleep=0.1, count=10)

        if verbose:
            print('Try again...')
        station.active(False)
        Pins.power_led.flash(sleep=0.1, count=20)
        Pins.power_led.off()
        station.active(True)

    print("ERROR: WiFi not connected! Password wrong?!?")
    Pins.power_led.flash(sleep=0.2, count=20)


def connect(station, verbose):
    Pins.power_led.flash(sleep=0.1, count=5)

    if verbose:
        print('read WiFi config...')

    # Rename old 'config.json' to new '_config_wifi.json'
    import os
    try:
        os.stat('config.json')  # Check if exists
    except OSError:
        pass
    else:
        os.rename('config.json', '_config_wifi.json')
    del os
    gc.collect()

    from config_files import get_json_config
    wifi_configs = get_json_config(key='wifi')

    del get_json_config
    del sys.modules['config_files']
    gc.collect()

    known_ssid = get_known_ssid(station, wifi_configs, verbose=verbose)
    if known_ssid is None:
        print('Skip Wifi connection.')
    else:
        return connect2ssid(
            station=station,
            ssid=known_ssid,
            password=wifi_configs[known_ssid],
            verbose=verbose
        )
