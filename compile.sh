#!/usr/bin/env bash

set -ex

PWD=$(pwd)

FROZEN_MANIFEST=${PWD}/manifest.py
FWBIN=${PWD}/build/firmware-combined.bin

(
    cd esp-open-sdk
    make STANDALONE=y
)
export PATH=${PATH}:${PWD}/esp-open-sdk/xtensa-lx106-elf/bin

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

