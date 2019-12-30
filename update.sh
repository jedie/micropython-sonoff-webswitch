#!/usr/bin/env bash

set -ex

git pull origin/master
pipenv update --dev
docker pull jedie/micropython:latest
