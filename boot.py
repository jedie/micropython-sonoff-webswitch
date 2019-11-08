# This file is executed on every boot (including wake-boot from deepsleep)
#import esp
#esp.osdebug(None)
#import uos
#uos.dupterm(None, 1) # disable REPL on UART(0)
import gc
gc.collect()

import machine
led_pin = machine.Pin(13, machine.Pin.OUT, value=0) # turn power LED on


import network
import ntptime


ap = network.WLAN(network.AP_IF) # create access-point interface
if ap.active():
    print('deactivate access-point interface...')
    ap.active(False)

wlan = network.WLAN(network.STA_IF) # create station interface
wlan.active(True)       # activate the interface
for info in wlan.scan():
    ssid, bssid, channel, RSSI, authmode, hidden = info
    ssid = ssid.decode("UTF-8")
    print('SSID:', ssid, '(channel:', channel, 'hidden:', hidden, ')')

if not wlan.isconnected():
    from get_config import config
    ssid = config['wifi']['ssid']
    print('Connect to Wifi access point:', ssid)    
    wlan.connect(ssid, config['wifi']['password'])
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