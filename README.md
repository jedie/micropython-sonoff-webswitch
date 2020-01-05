# micropython-sonoff-webswitch

![badge.svg](https://github.com/jedie/micropython-sonoff-webswitch/workflows/Run%20Tests/badge.svg?branch=master)
![badge.svg](https://github.com/jedie/micropython-sonoff-webswitch/workflows/Compile%20yaota8266.bin/badge.svg?branch=master)
![badge.svg](https://github.com/jedie/micropython-sonoff-webswitch/workflows/Compile%20MicroPython%20Firmware/badge.svg?branch=master)

MicroPython project to free the Sonoff WiFi Smart Socket from the cloud by run a webserver on the device.

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
* make OTA Update (timeout: 15sec.)
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
~/micropython-sonoff-webswitch$ make update
```

## compile own firmware

To see all make targets, just call make, e.g.:
```bash
~/micropython-sonoff-webswitch$ make
make targets:
  help               This help page
  docker-pull        pull docker images
  docker-build       pull and build docker images
  update             update git repositories/submodules, virtualenv, docker images and build local docker image
  test               Run pytest
  micropython_shell  start a bash shell in docker container "local/micropython:latest"
  unix-port-shell    start micropython unix port interpreter
  build-firmware     compiles the micropython firmware and store it here: /build/firmware-ota.bin
  yaota8266-rsa-keys Pull/build yaota8266 docker images and Generate RSA keys and/or print RSA modulus line for copy&paste into config.h
  yaota8266-build    Compile ota bootloader and store it here: build/yaota8266.bin
  flash-yaota8266    Flash build/yaota8266.bin to location 0x0 via esptool.py
  flash-firmware     Flash build/firmware-ota.bin to location 0x3c000 via esptool.py
  live-ota           Start ota_client.py to OTA Update the firmware file build/firmware-ota.bin via yaota8266
```

### docker-yaota8266/yaota8266/config.h

You must create `docker-yaota8266/yaota8266/config.h` and insert your RSA modulus line.

To generate your RSA keys and display the needed line for `config.h` just call:
```bash
~/micropython-sonoff-webswitch$ make yaota8266-rsa-keys
...
Copy&paste this RSA modulus line into your config.h:
----------------------------------------------------------------------------------------------------
#define MODULUS "\xce\x4a\xaf\x65\x0d\x4a\x74\xda\xc1\x30\x59\x80\xcf\xdd\xe8\x2a\x2e\x1d\xf7\xa8\xc9\x6c\xa9\x4a\x2c\xb7\x8a\x5a\x2a\x25\xc0\x2b\x7b\x2f\x58\x4c\xa8\xcb\x82\x07\x06\x08\x7e\xff\x1f\xce\x47\x13\x67\x94\x5f\x9a\xac\x5e\x7d\xcf\x63\xf0\x08\xe9\x51\x98\x95\x01"
----------------------------------------------------------------------------------------------------
```

The generated RSA key files are here:

* `docker-yaota8266/yaota8266/ota-client/priv.key`
* `docker-yaota8266/yaota8266/ota-client/pub.key`

You should backup theses files;


### compile

After you have created your own RSA keys and `config.h`, you can compile `yaota8266.bin` and `firmware-ota.bin`, e.g.:
```bash
~/micropython-sonoff-webswitch$ make yaota8266-build
~/micropython-sonoff-webswitch$ make build-firmware
```

The compiled files are stored here:

* `~/micropython-sonoff-webswitch/build/yaota8266.bin`
* `~/micropython-sonoff-webswitch/build/firmware-ota.bin`

### flash yaota8266 and firmware

After you have called `make yaota8266-build` and `make build-firmware` you can flash your device:

```bash
~/micropython-sonoff-webswitch$ make flash-yaota8266
~/micropython-sonoff-webswitch$ make flash-firmware
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

**Importand**:

The micropython version and the `mpy_cross` version must be **the same**!
Otherwise the compiled `.mpy` can't run on the device!

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
import time, network
sta_if = network.WLAN(network.STA_IF)
sta_if.active(True)
sta_if.connect('your-ssid', 'Your-WiFi-Password')
while not sta_if.isconnected():
    time.sleep(0.5)
print('connected, ok.')
```

### OTA updates

**Note**: There are two kinds of OTA updates:

* 'hard' OTA update via **yaota8266** bootloader that will replace the complete firmware.
* 'soft' OTA updates via pure micropython script that will only upload new files to the flash filesystem.

The 'hard' OTA via **yaota8266** is work-in-progress and will currenlty not work, see: https://github.com/jedie/micropython-sonoff-webswitch/issues/33

#### 'soft' OTA updates

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

* compare device micropython version with installed `mpy_cross` version (If not match: deny update)
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

### sub project links

* Compile `yaota8266.bin` via docker: https://github.com/jedie/docker-yaota8266
* Compile micropython firmware via docker: https://github.com/jedie/docker-micropython

### Forum links

* OTA updates: https://forum.micropython.org/viewtopic.php?f=2&t=7300
* free RAM: https://forum.micropython.org/viewtopic.php?f=2&t=7345

### misc

* S20 Wifi Smart Socket Schematic: https://www.itead.cc/wiki/S20_Smart_Socket
