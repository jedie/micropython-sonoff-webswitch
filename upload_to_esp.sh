#!/bin/bash

export AMPY_BAUD=115200
export AMPY_PORT=/dev/ttyUSB0

set -ex

pipenv run ampy put src /
pipenv run ampy ls
pipenv run ampy reset