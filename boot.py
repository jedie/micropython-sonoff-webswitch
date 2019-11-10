# This file is executed on every boot (including wake-boot from deepsleep)
#import esp
#esp.osdebug(None)
#import uos
#uos.dupterm(None, 1) # disable REPL on UART(0)
import gc
gc.collect()

import time
import machine
led_pin = machine.Pin(13, machine.Pin.OUT, value=0) # turn power LED on


import network
import ntptime


ap = network.WLAN(network.AP_IF) # create access-point interface
if ap.active():
    print('deactivate access-point interface...')
    ap.active(False)

wlan = network.WLAN(network.STA_IF) # create station interface
#wlan.active(False)     # uncomment to force reconnection
wlan.active(True)       # activate the interface

def get_known_ssid(wlan, config):
    print('Scan WiFi...')
    
    auth_mode_dict={
        0:"open",
        1:"WEP",
        2:"WPA-PSK",
        3:"WPA2-PSK",
        4:"WPA/WPA2-PSK",
    }
    known_ssid = None
    for no in range(3):
        for info in wlan.scan():
            ssid, bssid, channel, RSSI, auth_mode, hidden = info
            auth_mode = auth_mode_dict.get(auth_mode, auth_mode)
            ssid = ssid.decode("UTF-8")
            print('SSID:', ssid, '(channel:', channel, 'authmode:', auth_mode, 'hidden:', hidden, ')')
            if ssid in wifi_configs:
                known_ssid = ssid
        if known_ssid is not None:
            return known_ssid
    print('ERROR: No known WiFi found!')


def connect(wlan, ssid, password):
    status_dict={
        network.STAT_IDLE:'no connection and no activity',
        network.STAT_CONNECTING:'connecting in progress',
        network.STAT_WRONG_PASSWORD:'failed due to incorrect password',
        network.STAT_NO_AP_FOUND:'failed because no access point replied',
        network.STAT_CONNECT_FAIL:'failed due to other problems',
        network.STAT_GOT_IP:'connection successful',
    }
    for no in range(0,3):
        print('PHY mode:', network.phy_mode())
        print('Connect to Wifi access point:', ssid, repr(password))
        wlan.connect(ssid, password)
        for x in range(30):
            status = wlan.status()
            status_text = status_dict[status]
            print(status_text)
            if status == network.STAT_GOT_IP:
                return
            elif status == network.STAT_WRONG_PASSWORD:
                return
            print('wait...')
            time.sleep(1)

        if wlan.isconnected():
            print('Connected to:', ssid)
            return
        else:
            print('Try again...')
            led_pin.value(1) # turn power LED off
            wlan.active(False)
            time.sleep(2)
            led_pin.value(0) # turn power LED on
            wlan.active(True)
    print("ERROR: WiFi not connected! Password wrong?!?")


if not wlan.isconnected():
    from get_config import config
    wifi_configs = config['wifi']
    
    ssid = get_known_ssid(wlan, config)
    if ssid is None:
        print('Skip Wifi connection.')
    else:
        connect(wlan, ssid, password=config['wifi'][ssid])
            
else:
    print('already connected!')
    
#print('MAC:', wlan.config('mac'))
print('IP/netmask/gw/DNS addresses:', wlan.ifconfig())


print('set the rtc datetime from the remote server...')
try:
    ntptime.settime()
except OSError as err:
    print('Error set time from ntp server:', err)

rtc = machine.RTC()
print('UTC:', rtc.datetime()) 



led_pin.value(1) # turn power LED off