# micropython-sonoff-webswitch

Minimal MicroPython project to get a webserver on Sonoff WiFi Smart Socket.

Very good information to get startet can you found here:

https://github.com/tsaarni/mqtt-micropython-smartsocket

Tested devices:

* Sonoff S20 (Easy to connect. Solder joints prepared.)
* Sonoff S26 (Harder to connect: Solder joints very small.)


## prepare

* Flash last MicroPython to your device, see: http://docs.micropython.org/en/latest/esp8266/tutorial/intro.html
* Find a way to start a python script file on the device via REPL: http://docs.micropython.org/en/latest/esp8266/tutorial/repl.html


## quickstart

Clone the sources, compile them with [mpy-cross](https://pypi.org/project/mpy-cross/) and start the OTA Update server:
```bash
~$ git clone https://github.com/jedie/micropython-sonoff-webswitch.git
~$ cd micropython-sonoff-webswitch
~/micropython-sonoff-webswitch$ pipenv sync
~/micropython-sonoff-webswitch$ pipenv run start_ota_server.py 
```

* Create a `src/config.json` with your WiFi SSID/password ([See example file](https://github.com/jedie/micropython-sonoff-webswitch/blob/master/config.json))
* With a new, fresh, empty device, start the [/src/ota_client.py](https://github.com/jedie/micropython-sonoff-webswitch/blob/master/src/ota_client.py) on the device script manually.

The 'ota_client.py' will download all files from the 'OTA Server' and reboot the device.

If everything is fine, the device will do this:

* boot
* connect to your WiFi
* get current time via ntp
* make OTA Update
* serve web page

Point you Webserver to the IP from the device.

You can turn the switch on/off by the web page or the device button.
Reset the device by long pressing the button.


## Screenshot

The Web Page looks like this:

![Screenshot_2019-12-02 Sonoff S20.png](https://raw.githubusercontent.com/jedie/micropython-sonoff-webswitch/master/Screenshot_2019-12-02%20Sonoff%20S20.png)


## References

* S20 Wifi Smart Socket Schematic: https://www.itead.cc/wiki/S20_Smart_Socket


## Forum links

* OTA updates: https://forum.micropython.org/viewtopic.php?f=2&t=7300
* free RAM: https://forum.micropython.org/viewtopic.php?f=2&t=7345
