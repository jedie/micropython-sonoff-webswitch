DOCKER_UID=$(shell id -u)
DOCKER_UGID=$(shell id -g)
PWD=$(shell pwd)


default: help


help:  ## This help page
	@echo 'make targets:'
	@grep -E '^[a-zA-Z0-9_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "  %-18s %s\n", $$1, $$2}'


docker-pull:  ## pull docker images
	docker pull jedie/micropython:latest


docker-build: docker-pull  ## pull and build docker images
	docker build \
    --build-arg "DOCKER_UID=${DOCKER_UID}" \
    --build-arg "DOCKER_UGID=${DOCKER_UGID}" \
    firmware_scripts/. \
    -t local/micropython:latest


update: docker-build  ## update git repositories/submodules, docker images and build local docker images
	git pull origin master
	git submodule update --init --recursive
	pipenv sync


micropython_shell: docker-build  ## start a bash shell in docker container "local/micropython:latest"
	docker run -it \
		-e "DOCKER_UID=${DOCKER_UID}" \
		-e "DOCKER_UGID=${DOCKER_UGID}" \
		--mount type=bind,src=${PWD}/firmware_scripts/,dst=/mpy/firmware_scripts/ \
		--mount type=bind,src=${PWD}/sdist/,dst=/mpy/micropython/ports/esp8266/sdist/ \
		--mount type=bind,src=${PWD}/build/,dst=/mpy/build/ \
		local/micropython:latest \
		/bin/bash


unix-port-shell: docker-build  ## start micropython unix port interpreter
	docker run -it \
		-e "DOCKER_UID=${DOCKER_UID}" \
		-e "DOCKER_UGID=${DOCKER_UGID}" \
		local/micropython:latest \
		/mpy/micropython/ports/unix/micropython


compile-firmware: docker-build  ## compiles the micropython firmware and store it here: /build/firmware-ota.bin
	mkdir -p sdist
	cp -u src/*.py sdist/

	rm sdist/__init__.py
	rm sdist/boot.py
	rm sdist/main.py

	docker run \
		-e "DOCKER_UID=${DOCKER_UID}" \
		-e "DOCKER_UGID=${DOCKER_UGID}" \
		--mount type=bind,src=${PWD}/firmware_scripts/,dst=/mpy/firmware_scripts/ \
		--mount type=bind,src=${PWD}/sdist/,dst=/mpy/micropython/ports/esp8266/sdist/ \
		--mount type=bind,src=${PWD}/build/,dst=/mpy/build/ \
		local/micropython:latest \
		/bin/bash -c "cd /mpy/micropython/ports/esp8266/ \
			&& make clean \
			&& make -j12 ota \
				FROZEN_MANIFEST=/mpy/firmware_scripts/manifest.py \
				MICROPY_VFS_FAT=0 \
				MICROPY_VFS_LFS2=1 \
			&& cp -u /mpy/micropython/ports/esp8266/build-GENERIC/firmware-ota.bin /mpy/build/firmware-ota.bin"


yaota8266-rsa-keys: update  ## Pull/build yaota8266 docker images and Generate RSA keys and/or print RSA modulus line for copy&paste into config.h
	$(MAKE) -C docker-yaota8266 rsa-keys


yaota8266-compile: update  ## Compile ota bootloader and store it here: build/yaota8266.bin
	$(MAKE) -C docker-yaota8266 compile
	cp -u docker-yaota8266/yaota8266/yaota8266.bin build/yaota8266.bin


flash-yaota8266:  ## Flash build/yaota8266.bin to location 0x0 via esptool.py
	@if [ -f build/yaota8266.bin ] ; \
	then \
		echo -n "\nbuild/yaota8266.bin exists, ok.\n\n" ; \
	else \
		echo -n "\nERROR: Please run 'make yaota8266-compile' first to create 'build/yaota8266.bin' !\n\n" ; \
		exit 1 ; \
	fi
	pipenv run esptool.py --port /dev/ttyUSB0 --baud 460800 write_flash -fs 1MB -fm dout 0x0 build/yaota8266.bin


flash-firmware:  ## Flash build/firmware-ota.bin to location 0x3c000 via esptool.py
	@if [ -f build/firmware-ota.bin ] ; \
	then \
		echo -n "\nbuild/firmware-ota.bin exists, ok.\n\n" ; \
	else \
		echo -n "\nERROR: Please run 'make compile-firmware' first to create 'build/firmware-ota.bin' !\n\n" ; \
		exit 1 ; \
	fi
	pipenv run esptool.py --port /dev/ttyUSB0 --baud 460800 write_flash -fs 1MB -fm dout 0x3c000 build/firmware-ota.bin
