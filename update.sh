#!/usr/bin/env bash

set -ex

pipenv update --dev
git submodule update --init --recursive

(
    cd micropython
    git fetch
    git checkout origin/master
    git submodule update --init
)
(
    cd micropython-lib
    git fetch
    git checkout origin/master
)
(
    cd esp-open-sdk
    git fetch
    git checkout origin/master
)
