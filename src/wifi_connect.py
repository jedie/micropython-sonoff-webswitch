
# import sys

import network
import utime


def get_known_ssid(station, wifi_configs):
    print('Scan WiFi...')
    from pins import Pins

    known_ssid = None
    for no in range(3):
        for info in station.scan():
            Pins.power_led.toggle()
            ssid, bssid, channel, RSSI, auth_mode, hidden = info
            ssid = ssid.decode("UTF-8")
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


def connect2ssid(station, ssid, password):
    from pins import Pins
    for no in range(0, 3):
        print('PHY mode: %s' % network.phy_mode())
        # print('Connect to Wifi access point:', ssid, repr(password))
        print('Connect to Wifi access point: %s' % ssid)
        Pins.power_led.toggle()
        station.connect(ssid, password)
        for wait_sec in range(30, 1, -1):
            status = station.status()
            if status == network.STAT_GOT_IP:
                Pins.power_led.on()
                print(
                    'Connected to station IP/netmask/gw/DNS addresses:', station.ifconfig()
                )
                return utime.time()
            elif status == network.STAT_WRONG_PASSWORD:
                print('Wrong password!')
                return
            print('wait %i...' % wait_sec)
            Pins.power_led.flash(sleep=0.1, count=10)

        print('Try again...')
        station.disconnect()
        station.active(False)
        Pins.power_led.flash(sleep=0.1, count=20)
        Pins.power_led.off()
        station.active(True)

    print("ERROR: WiFi not connected! Password wrong?!?")
    Pins.power_led.flash(sleep=0.2, count=20)


def set_dhcp_hostname(station):
    print('Set WiFi DHCP hostname to:', end=' ')
    from device_name import get_device_name
    device_name = get_device_name()

    # del get_device_name
    # del sys.modules['device_name']

    print(repr(device_name))
    station.config(dhcp_hostname=device_name)


def connect(station):
    station.active(True)  # activate the interface

    from pins import Pins
    Pins.power_led.flash(sleep=0.1, count=5)

    print('read WiFi config...')

    # Rename old 'config.json' to new '_config_wifi.json'
    import os
    try:
        os.stat('config.json')  # Check if exists
    except OSError:
        pass
    else:
        os.rename('config.json', '_config_wifi.json')
    # del os

    from config_files import get_json_config
    wifi_configs = get_json_config(key='wifi')

    # del get_json_config
    # del sys.modules['config_files']

    if wifi_configs is None:
        raise RuntimeError('Empty WiFi settings! Please upload you WiFi config file!')

    set_dhcp_hostname(station)

    try:
        known_ssid = get_known_ssid(station, wifi_configs)
    except OSError as e:
        print('Error get known SSID:', e)  # e.g.: 'scan failed'
        Pins.power_led.flash(sleep=0.4, count=20)
        return

    if known_ssid is None:
        print('Skip Wifi connection.')
    else:
        return connect2ssid(
            station=station,
            ssid=known_ssid,
            password=wifi_configs[known_ssid],
        )


if __name__ == '__main__':
    # Connect or reconnect
    sta_if = network.WLAN(network.STA_IF)
    sta_if.disconnect()
    connect(station=sta_if)
    print('connected:', sta_if.isconnected())
