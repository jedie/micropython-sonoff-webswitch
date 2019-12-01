# micropython-sonoff-webswitch

Minimal microPython project to get a webserver on Sonoff WiFi Smart Socket.

Very good information to get startet can you found here:

https://github.com/tsaarni/mqtt-micropython-smartsocket

Tested devices:

* Sonoff S20 (Easy to connect. Solder joints prepared.)
* Sonoff S26 (Harder to connect: Solder joints very small.)


## quickstart

Create a `src/config.json` with your WiFi SSID/password (See example file)

run e.g.:
```bash
pipenv sync
./upload_to_esp.sh
```

The device will do:

* boot
* connect to your WiFi
* get current time via ntp
* serve web page

Point you Webserver to the IP from the device.

You can turn the switch on/off by the web page or the device button.
Reset the device by long pressing the button.

## OTA

The device will update the source codes `over the air` on startup.
You must start the server on your host. Just run:
```bash
.../micropython-sonoff-webswitch$ python3 ./ota_server.py 
```
After server start: Start the device.


## Screenshot

The Web Page looks like this:

![Screenshot_2019-12-02 Sonoff S20.png](https://raw.githubusercontent.com/jedie/micropython-sonoff-webswitch/master/Screenshot_2019-12-02%20Sonoff%20S20.png)


## References

S20 Wifi Smart Socket Schematic https://www.itead.cc/wiki/S20_Smart_Socket
