#!/usr/bin/env bash

set -x

pipenv update --dev
cd micropython
git fetch
git checkout origin/master
