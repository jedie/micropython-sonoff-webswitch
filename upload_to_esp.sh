#!/bin/bash

set -ex

pipenv run ampy --port=/dev/ttyUSB0 put src /
pipenv run ampy --port=/dev/ttyUSB0 ls
pipenv run ampy --port=/dev/ttyUSB0 reset
