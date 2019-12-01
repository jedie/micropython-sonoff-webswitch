"""
    OTA Client for micropython devices
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    Connect to OTA Server and run commands from him
    to update local files.

    This script must be run on the micropython device.
"""
import gc
import sys

import machine
import network
import uasyncio as asyncio
import ubinascii as binascii
import uhashlib as hashlib
import uos as os
import utime as time

_SOCKET_TIMEOUT = const(10)
_PORT = const(8266)
_CHUNK_SIZE = const(512)
_BUFFER = bytearray(_CHUNK_SIZE)
_FILE_TYPE = const(0x8000)


def reset(reason):
    print('Reset because: %s' % reason)
    # for no in range(3, 1, -1):
    #     print('Hard reset device in %i sec...' % no)
    #     time.sleep(1)
    machine.reset()
    time.sleep(1)
    sys.exit(-1)


class OtaClient:
    async def read_line_string(self, reader):
        data = await reader.readline()
        return data.rstrip(b'\n').decode('utf-8')

    async def write_line_string(self, writer, text):
        await writer.awrite(b'%s\n' % text.encode('utf-8'))

    async def error(self, writer, text):
        print('ERROR: %s' % text)
        await self.write_line_string(writer, text)
        reset(text)

    async def __call__(self, reader, writer):
        address = writer.get_extra_info('peername')
        print('Accepted connection from %s:%s' % address)
        while True:
            command = await self.read_line_string(reader)
            print('Receive command:', command)
            if not command:
                reset('Empty command?!?')

            command = 'command_%s' % command
            if command == 'command_exit':
                print('exit!')
                await self.command_send_ok(reader, writer)
                sys.exit(0)

            gc.collect()
            try:
                func = getattr(self, command)
            except AttributeError as e:
                sys.print_exception(e)
                await self.error(writer, 'Command unknown')
            else:
                print('call:', command)
                try:
                    await func(reader, writer)
                except Exception as e:
                    sys.print_exception(e)
                    await self.error(writer, 'Command error')

    async def command_send_ok(self, reader, writer):
        await self.write_line_string(writer, 'OK')

    async def command_chunk_size(self, reader, writer):
        await self.write_line_string(writer, '%i' % _CHUNK_SIZE)

    async def command_files_info(self, reader, writer):
        print('Send files info...')
        for name, file_type, inode, size in os.ilistdir():
            if file_type != _FILE_TYPE:
                print(' *** Skip: %s' % name)
                continue

            await writer.awrite(b'%s\r%i\r' % (name, size))

            sha256 = hashlib.sha256()
            with open(name, 'rb') as f:
                while True:
                    count = f.readinto(_BUFFER, _CHUNK_SIZE)
                    if count < _CHUNK_SIZE:
                        sha256.update(_BUFFER[:count])
                        break
                    else:
                        sha256.update(_BUFFER)

            await writer.awrite(binascii.hexlify(sha256.digest()))
            await writer.awrite(b'\r\n')
        await writer.awrite(b'\n\n')
        print('Files info sended, ok.')

    async def command_receive_file(self, reader, writer):
        """
        Store a new/updated file on local micropython device.
        """
        print('receive file', end=' ')
        file_name = await self.read_line_string(reader)
        file_size = int(await self.read_line_string(reader))
        file_sha256 = await self.read_line_string(reader)
        await self.command_send_ok(reader, writer)
        print('%r %i Bytes SHA256: %s' % (file_name, file_size, file_sha256))

        temp_file_name = '%s.temp' % file_name
        try:
            with open(temp_file_name, 'wb') as f:
                sha256 = hashlib.sha256()
                received = 0
                while True:
                    print('.', end='')
                    data = await reader.read(_CHUNK_SIZE)
                    if not data:
                        await self.error(writer, 'No file data')

                    f.write(data)
                    sha256.update(data)
                    received += len(data)
                    if received >= file_size:
                        print('completed!')
                        break

            print('Received %i Bytes' % received, end=' ')

            local_file_size = os.stat(temp_file_name)[6]
            if local_file_size != file_size:
                await self.error(writer, 'Size error!')

            hexdigest = binascii.hexlify(sha256.digest()).decode('utf-8')
            if hexdigest == file_sha256:
                print('Hash OK:', hexdigest)
                try:
                    os.remove(file_name)
                except OSError:
                    pass  # e.g.: new file that doesn't exist, yet.

                os.rename(temp_file_name, file_name)

                print('Compare written file content', end=' ')
                sha256 = hashlib.sha256()
                with open(file_name, 'rb') as f:
                    while True:
                        count = f.readinto(_BUFFER, _CHUNK_SIZE)
                        if count < _CHUNK_SIZE:
                            sha256.update(_BUFFER[:count])
                            break
                        else:
                            sha256.update(_BUFFER)

                hexdigest = binascii.hexlify(sha256.digest()).decode('utf-8')
                if hexdigest == file_sha256:
                    print('Hash OK:', hexdigest)
                    await self.command_send_ok(reader, writer)
                    return

            await self.error(writer, 'Hash error: %s' % hexdigest)
        finally:
            print('Remove temp file')
            try:
                os.remove(temp_file_name)
            except OSError:
                pass


def assert_wlan_is_active():
    for interface_type in (network.AP_IF, network.STA_IF):
        wlan = network.WLAN(interface_type)
        if wlan.active():
            if wlan.isconnected():
                print('Connected to station IP/netmask/gw/DNS addresses:', wlan.ifconfig())
                return True

    raise AssertionError('WiFi not active and connected!')


def do_ota_update():
    gc.collect()
    print('Start web server on port:', _PORT)
    assert_wlan_is_active()
    gc.collect()

    loop = asyncio.get_event_loop()
    loop.create_task(asyncio.start_server(OtaClient(), '0.0.0.0', _PORT))
    print('run forever...')
    try:
        loop.run_forever()
    except Exception as e:
        sys.print_exception(e)
    except SystemExit as e:
        if e.args[0] == 0:
            print('OTA Update complete successfully')
            sys.exit()
        reset('Unknown sys exit code.')
    reset('OTA unknown error')


if __name__ == '__main__':
    do_ota_update()
