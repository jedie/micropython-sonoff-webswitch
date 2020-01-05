DOCKER_UID=$(shell id -u)
DOCKER_UGID=$(shell id -g)
PWD=$(shell pwd)

default: help


help:  ## This help page
	@echo 'make targets:'
	@grep -E '^[a-zA-Z0-9_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "  %-24s %s\n", $$1, $$2}'


docker-pull:  ## pull docker images
	docker pull jedie/micropython:latest


docker-build: docker-pull  ## pull and build docker images
	docker build \
		--build-arg "DOCKER_UID=${DOCKER_UID}" \
		--build-arg "DOCKER_UGID=${DOCKER_UGID}" \
		. \
		-t local/micropython:latest
	#
	# Just "extract" compiled "mpy-cross" from docker image and store it here: ./build/mpy-cross
	# So we can use it locally for 'soft' OTA Updates
	docker run \
		-e "DOCKER_UID=${DOCKER_UID}" \
		-e "DOCKER_UGID=${DOCKER_UGID}" \
		--mount type=bind,src=${PWD}/build/,dst=/mpy/build/ \
		local/micropython:latest \
		/bin/bash -c "cp /mpy/micropython/mpy-cross/mpy-cross /mpy/build/mpy-cross"
	#
	# Print version info:
	build/mpy-cross --version


update: docker-build  ## update git repositories/submodules, virtualenv, docker images and build local docker image
	git pull origin master
	@if [ -d docker-yaota8266/yaota8266/ota-server/lib/axtls ] ; \
	then \
		echo -n "\nGit submodules exists, ok.\n\n" ; \
	else \
		git submodule update --init --recursive ; \
	fi
	python3 -m pip install --upgrade pipenv
	pipenv sync


test: update  ## Run pytest
	PYTHONPATH=src pipenv run pytest


.PHONY: sdist
sdist:
	python3 utils/make_sdist.py


micropython_shell: sdist docker-build  ## start a bash shell in docker container "local/micropython:latest"
	docker run -it \
		-e "DOCKER_UID=${DOCKER_UID}" \
		-e "DOCKER_UGID=${DOCKER_UGID}" \
		--mount type=bind,src=${PWD}/micropython_config/,dst=/mpy/micropython_config/ \
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


assert-yaota8266-setup:
	@if [ -f docker-yaota8266/yaota8266/config.h ] ; \
	then \
		echo -n "\ndocker-yaota8266/yaota8266/config.h exists, ok.\n\n" ; \
	else \
		echo -n "\nERROR: Please create 'docker-yaota8266/yaota8266/config.h' first!\n\n" ; \
		exit 1 ; \
	fi

	@if [ -f docker-yaota8266/yaota8266/ota_client/priv.key ] ; \
	then \
		echo -n "\ndocker-yaota8266/yaota8266/ota_client/priv.key exists, ok.\n\n" ; \
	else \
		echo -n "\nERROR: RSA priv.key not found! Please call 'make yaota8266-rsa-keys' first!\n\n" ; \
		exit 1 ; \
	fi


build-firmware-combined: sdist docker-build  ## compiles the micropython non-OTA firmware and store it here: /build/firmware-combined.bin
	docker run \
		-e "DOCKER_UID=${DOCKER_UID}" \
		-e "DOCKER_UGID=${DOCKER_UGID}" \
		--mount type=bind,src=${PWD}/micropython_config/,dst=/mpy/micropython_config/ \
		--mount type=bind,src=${PWD}/sdist/,dst=/mpy/micropython/ports/esp8266/sdist/ \
		--mount type=bind,src=${PWD}/build/,dst=/mpy/build/ \
		local/micropython:latest \
		/bin/bash -c "cd /mpy/micropython/ports/esp8266/ \
			&& make clean \
			&& make -j12 \
				FROZEN_MANIFEST=/mpy/micropython_config/manifest.py \
				MICROPY_PY_BTREE=0 \
				MICROPY_VFS_FAT=0 \
				MICROPY_VFS_LFS2=1 \
			&& cp -u /mpy/micropython/ports/esp8266/build-GENERIC/firmware-combined.bin /mpy/build/firmware-combined.bin"
	@echo -n "\n"
	ls -la build
	@echo -n "\n"
	file build/firmware-combined.bin

build-ota-firmware: sdist docker-build assert-yaota8266-setup  ## compiles the micropython OTA firmware and store it here: /build/firmware-ota.bin
	docker run \
		-e "DOCKER_UID=${DOCKER_UID}" \
		-e "DOCKER_UGID=${DOCKER_UGID}" \
		--mount type=bind,src=${PWD}/micropython_config/,dst=/mpy/micropython_config/ \
		--mount type=bind,src=${PWD}/sdist/,dst=/mpy/micropython/ports/esp8266/sdist/ \
		--mount type=bind,src=${PWD}/build/,dst=/mpy/build/ \
		local/micropython:latest \
		/bin/bash -c "cd /mpy/micropython/ports/esp8266/ \
			&& make clean \
			&& make -j12 ota \
				FROZEN_MANIFEST=/mpy/micropython_config/manifest.py \
				MICROPY_PY_BTREE=0 \
				MICROPY_VFS_FAT=0 \
				MICROPY_VFS_LFS2=1 \
			&& cp -u /mpy/micropython/ports/esp8266/build-GENERIC/firmware-ota.bin /mpy/build/firmware-ota.bin"
	@echo -n "\n"
	python3 docker-yaota8266/yaota8266/ota-client/ota_client.py sign build/firmware-ota.bin
	@echo -n "\n"
	ls -la build
	@echo -n "\n"
	file build/firmware-ota.bin


yaota8266-rsa-keys: docker-build  ## Pull/build yaota8266 docker images and Generate RSA keys and/or print RSA modulus line for copy&paste into config.h
	$(MAKE) -C docker-yaota8266 rsa-keys


yaota8266-build: docker-build assert-yaota8266-setup  ## Compile ota bootloader and store it here: build/yaota8266.bin
	$(MAKE) -C docker-yaota8266 build
	@echo -n "\n"
	cp -u docker-yaota8266/yaota8266/yaota8266.bin build/yaota8266.bin
	ls -la build
	@echo -n "\n"
	file build/yaota8266.bin


erase-flash:  ## call esptool.py erase_flash
	pipenv run esptool.py --port /dev/ttyUSB0 erase_flash

flash-firmware-combined:  ## Flash build/firmware-combined to location 0x3c000 via esptool.py
	@if [ -f build/firmware-combined.bin ] ; \
	then \
		echo -n "\nbuild/firmware-combined.bin exists, ok.\n\n" ; \
	else \
		echo -n "\nERROR: Please run 'make build-firmware-combined' first to create 'build/firmware-combined.bin' !\n\n" ; \
		exit 1 ; \
	fi
	pipenv run esptool.py --port /dev/ttyUSB0 --baud 460800 write_flash -fs 1MB -fm dout 0 build/firmware-combined.bin


flash-yaota8266:  ## Flash build/yaota8266.bin to location 0x0 via esptool.py
	@if [ -f build/yaota8266.bin ] ; \
	then \
		echo -n "\nbuild/yaota8266.bin exists, ok.\n\n" ; \
	else \
		echo -n "\nERROR: Please run 'make yaota8266-build' first to create 'build/yaota8266.bin' !\n\n" ; \
		exit 1 ; \
	fi
	pipenv run esptool.py --port /dev/ttyUSB0 --baud 460800 write_flash -fs 1MB -fm dout 0x0 build/yaota8266.bin


flash-ota-firmware:  ## Flash build/firmware-ota.bin to location 0x3c000 via esptool.py
	@if [ -f build/firmware-ota.bin ] ; \
	then \
		echo -n "\nbuild/firmware-ota.bin exists, ok.\n\n" ; \
	else \
		echo -n "\nERROR: Please run 'make build-ota-firmware' first to create 'build/firmware-ota.bin' !\n\n" ; \
		exit 1 ; \
	fi
	pipenv run esptool.py --port /dev/ttyUSB0 --baud 460800 write_flash -fs 1MB -fm dout 0x3c000 build/firmware-ota.bin

live-ota:  ## Start ota_client.py to OTA Update the firmware file build/firmware-ota.bin via yaota8266
	python3 docker-yaota8266/yaota8266/ota-client/ota_client.py live-ota build/firmware-ota.bin.ota