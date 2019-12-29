#!/usr/bin/env bash

set -x

FROZEN_MANIFEST='$(pwd)/manifest.py'
FWBIN='$(pwd)/build/firmware-combined.bin'

cd micropython/ports/esp8266

make clean
make -j 8 FROZEN_MANIFEST=${FROZEN_MANIFEST} FWBIN=${FWBIN}
ls -la build
