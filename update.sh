#!/usr/bin/env bash

set -x

pipenv update --dev
git submodule update --init

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

wget --timestamp https://github.com/jepler/esp-open-sdk/releases/download/2018-06-10/xtensa-lx106-elf-standalone.tar.gz
#sha256sum xtensa-lx106-elf-standalone.tar.gz > xtensa-lx106-elf-standalone.tar.gz.sha256
sha256sum -c xtensa-lx106-elf-standalone.tar.gz.sha256
zcat xtensa-lx106-elf-standalone.tar.gz | tar x
