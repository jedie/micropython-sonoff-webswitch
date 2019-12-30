#!/bin/bash

# used docker image made via: https://github.com/jedie/docker-micropython

DOCKER_UID=$(id -u)
DOCKER_UGID=$(id -g)
PWD=$(pwd)

set -ex

mkdir -p sdist
cp src/*.py sdist/

rm sdist/__init__.py
rm sdist/boot.py
rm sdist/main.py

docker run \
    -e "DOCKER_UID=${DOCKER_UID}" \
    -e "DOCKER_UGID=${DOCKER_UGID}" \
    --mount type=bind,src=${PWD}/firmware_scripts/,dst=/mpy/firmware_scripts/ \
    --mount type=bind,src=${PWD}/sdist/,dst=/mpy/micropython/ports/esp8266/sdist/ \
    --mount type=bind,src=${PWD}/build/,dst=/build/ \
    local/micropython:latest \
    /bin/bash /mpy/firmware_scripts/compile_firmware.sh



