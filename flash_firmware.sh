#!/usr/bin/env bash

# http://docs.micropython.org/en/latest/esp8266/tutorial/intro.html#deploying-the-firmware
#
# Download firmware from:
#
# http://micropython.org/download#esp8266
#
# setup user rights:
#
# sudo usermod -G dialout -a $USER
#
# 1. press and hold power button
# 2. then, connect to PC
# 3. start this script
#
#
# First "erase_flash" is needed, then "write_flash"
# but both steps need the reconnect to PC !
#

set -ex

#FIRMWARE='esp8266-20190529-v1.12.bin'
#
#wget --timestamp http://micropython.org/resources/firmware/${FIRMWARE}
#
#sha256sum ${FIRMWARE} > ${FIRMWARE}.sha256
#sha256sum -c ${FIRMWARE}.sha256

FIRMWARE='build/firmware-combined.bin'

#pipenv run esptool.py --port /dev/ttyUSB0 erase_flash
pipenv run esptool.py --port /dev/ttyUSB0 --baud 460800 write_flash -fs 1MB -fm dout 0x0 ${FIRMWARE}
