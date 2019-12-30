#!/bin/bash

if [[ ! -f "/.dockerenv" ]]; then
    echo "Call me only in docker container!"
fi

FROZEN_MANIFEST=/mpy/firmware_scripts/manifest.py
FWBIN=/build/firmware-combined.bin

# We are inside the jedie/micropython container

echo "build the esp8266 firmware"
(
    set -ex
    cd /mpy/micropython/ports/esp8266/
    make -j12 FROZEN_MANIFEST=${FROZEN_MANIFEST} FWBIN=${FWBIN} MICROPY_VFS_FAT=0 MICROPY_VFS_LFS2=1
)
exit 0
