# micropython-sonoff-webswitch

Minimal microPython project to get a webserver on Sonoff S20 WiFi Smart Socket.

Very good information to get startet can you found here:

https://github.com/tsaarni/mqtt-micropython-smartsocket

## quickstart

* change `config.json` and insert your WiFi SSID/password
* push all file to S20

The device will do:

* boot
* connect to your WiFi
* get current time via ntp
* serve web page

Point you Webserver to the IP from the device.

You can turn the switch on/off by the web page or the device button.

## References

S20 Wifi Smart Socket Schematic https://www.itead.cc/wiki/S20_Smart_Socket
