#!/bin/bash

# used docker image made via: https://github.com/jedie/docker-micropython

DOCKER_UID=$(id -u)
DOCKER_UGID=$(id -g)

set -ex

docker build --pull \
    --build-arg "DOCKER_UID=${DOCKER_UID}" \
    --build-arg "DOCKER_UGID=${DOCKER_UGID}" \
    firmware_scripts/. \
    -t local/micropython:latest



