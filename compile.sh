#!/usr/bin/env bash

set -x

PWD=$(pwd)

FROZEN_MANIFEST=${PWD}/manifest.py
FWBIN=${PWD}/build/firmware-combined.bin


export PATH=${PATH}:${PWD}/xtensa-lx106-elf/bin

(
    cd micropython
    make -C mpy-cross
)
(
    cd micropython/ports/esp8266
    make clean
    make -j 8 FROZEN_MANIFEST=${FROZEN_MANIFEST} FWBIN=${FWBIN}
)
ls -la build

