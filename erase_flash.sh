#!/usr/bin/env bash

set -ex

pipenv run esptool.py --port /dev/ttyUSB0 erase_flash
