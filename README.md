# micropython-sonoff-webswitch

Minimal MicroPython project to get a webserver on Sonoff WiFi Smart Socket.

Tested devices:

* Sonoff S20 (Easy to connect. Solder joints prepared.)
* Sonoff S26 (Harder to connect: Solder joints very small.)


## Features

* web interface
* schedule multiple timers
* Handle time zones (set you time zone via web page)
* Display an editable device name (Helpful if you have more than one device ;) )
* The device name will also be used as DHCP hostname
* OTA updates (currently without directory support)
* turn the switch on/off by the web page or the device button
* checkbox for each day of the week where timers are active
* Reset the device by long pressing the button
* supports multiple WIFI credentials
* NTP sync

The device will do this on every boot:

* boot
* connect to your WiFi
* get current time via ntp
* make OTA Update
* serve web page

Some notes about the timer functionality:

The Device always tries to turn the power ON/OFF based on the current timer. Even after a power failure.
However, this only works correctly if the current time is set correctly by the RTC.
The current time is automatically retrieved from the Internet via NTP sync. At boot and also repeated after start.
Of course, this can only work if the device is connected to the Internet via WiFi ;)

You can "overwrite" the current timer at any time by pressing the button on the device.
This overwrite will stay until the next timer.
After a power failure the "overwrite" information is deleted and the timer regulates the power again.


## Roadmap

Things that will be implement in the near feature:

* Insert new WiFi settings via web page
* timer toggle flag to reverse: power is switched off during the specified periods

further away:

* different timers for every weekday
* Support directories via OTA Updates


## Screenshot


The Web Page looks like this:

![screenshot 1](https://raw.githubusercontent.com/jedie/jedie.github.io/master/screenshots/WebSwitch/2019-12-14%20Sonoff%20S20%20WebServer%20v0.8.1a.png)

![screenshot 2](https://raw.githubusercontent.com/jedie/jedie.github.io/master/screenshots/WebSwitch/2019-12-14%20Sonoff%20S20%20WebServer%20v0.8.1b.png)

![screenshot 3](https://raw.githubusercontent.com/jedie/jedie.github.io/master/screenshots/WebSwitch/2019-12-14%20Sonoff%20S20%20WebServer%20v0.8.1c.png)

![screenshot 4](https://raw.githubusercontent.com/jedie/jedie.github.io/master/screenshots/WebSwitch/2019-12-14%20Sonoff%20S20%20WebServer%20v0.8.1d.png)

![screenshot 5](https://raw.githubusercontent.com/jedie/jedie.github.io/master/screenshots/WebSwitch/2019-12-14%20Sonoff%20S20%20WebServer%20v0.8.1e.png)


All existing screenshots can be found here:

* [jedie.github.io/blob/master/screenshots/WebSwitch/](https://github.com/jedie/jedie.github.io/blob/master/screenshots/WebSwitch/README.creole)


## prepare

* Open the device
* make a connection with a UART-USB converter with 3.3V option and to the `3.3V`, `GND`, `TX` and `RX` pins

Very good information to get started can you found here: https://github.com/tsaarni/mqtt-micropython-smartsocket


## quickstart

Clone the sources, and setup virtualenv via `pipenv`:
```bash
~$ git clone https://github.com/jedie/micropython-sonoff-webswitch.git
~$ cd micropython-sonoff-webswitch
~/micropython-sonoff-webswitch$ pipenv sync
~/micropython-sonoff-webswitch$ pipenv run start_ota_server.py
```


## flash micropython

* Flash last MicroPython firmware to your device, see: http://docs.micropython.org/en/latest/esp8266/tutorial/intro.html

overview:

* Press and hold the power button before connecting
* Connect device via UART-USB converter
* Now you can release the button.
* To erase the Flash with esptool, call: `./erase_flash.sh`
* disconnect the device from PC and reconnect with pressed button again
* To flash micropython call: `./flash_firmware.sh` (This script will download micropython, if not already done and compares the sha256 hash)
* disconnect device and reconnect **without** pressing the power button

Notes: In my experience flashing the S20 needs `-fs 1MB -fm dout 0x0`.


## WiFi config

To connect the device with your WIFI it needs the SSID/password.
Several WLAN network access data can be specified.

Copy and edit [_config_wifi-example.json](https://github.com/jedie/micropython-sonoff-webswitch/blob/master/_config_wifi-example.json) to `src/_config_wifi.json`


## bootstrap

If micropython is on the device, only the sources and your WiFi credentials file needs to be uploaded.

This 'bootstrapping' can be done in different ways.


### bootstrap via USB

Connect device via TTL-USB-converter to your PC and run [upload_files.py](https://github.com/jedie/micropython-sonoff-webswitch/blob/master/upload_files.py)

This script will do this:

* compile `src` files with [mpy-cross](https://pypi.org/project/mpy-cross/) to `bdist`
* upload all files from `bdist` to the device via [mpycntrl](https://github.com/kr-g/mpycntrl)

The upload is a little bit slow. Bootstrap via WiFi is faster, see below:


### bootstrap via WiFi

overview:

* Connect the device to your WiFi network
* put your `_config_wifi.json` to the root of the device
* Run `ota_client.py` to upload all `*.mpy` compiled files

I used [thonny](https://github.com/thonny/thonny) for this. With thonny it's easy to upload the config file and execute scripts on the device.

To connect to your WiFi network, edit and run this:

```python
import network
sta_if = network.WLAN(network.STA_IF)
sta_if.active(True)
sta_if.connect('your-ssid', 'Your-WiFi-Password')
```

### OTA updates

After the initial setup and when everything is working and the device is connected to your wlan, you can use OTA updates.

The device will run the [/src/ota_client.py](https://github.com/jedie/micropython-sonoff-webswitch/blob/master/src/ota_client.py) on every boot.

The script waits some time for the OTA server and after the timeout the normal web server will be started.

To start the `OTA Server`, do this:

```bash
~$ cd micropython-sonoff-webswitch
~/micropython-sonoff-webswitch$ pipenv run start_ota_server.py
```

If server runs: reboot device and look to the output of the OTA server.

The OTA update implementation does:

* send only new/changed files
* remove existing `.py` file on the device if `.mpy` file was send
* replace existing files only after correct sha hash verify


## project structure

* `./bdist/` - Contains the compiled files that will be uploaded to the device.
* `./helpers/` - Some device tests/helper scripts for developing (normaly not needed)
* `./mpy_tests/` - tests that can be run on micropython device (will be also run by pytest with mocks)
* `./ota/` - source code of the OTA server
* `./src/` - device source files
* `./tests/` - some pytest files (run on host with CPython)
* `./utils/` - utils for local run (compile, code lint, sync with mpycntrl)
* `./start_ota_server.py` - Starts the local OTA server (will compile, lint the `src` files and create `bdist`)
* `./upload_files.py` - Upload files via USB (will compile, lint the `src` files and create `bdist`)


## Links

### Forum links

* OTA updates: https://forum.micropython.org/viewtopic.php?f=2&t=7300
* free RAM: https://forum.micropython.org/viewtopic.php?f=2&t=7345

### misc

* S20 Wifi Smart Socket Schematic: https://www.itead.cc/wiki/S20_Smart_Socket
