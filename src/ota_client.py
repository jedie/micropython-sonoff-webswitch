"""
    OTA Client for micropython devices
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    Wait for OTA Server and run commands from him
    to update local files.
"""
import gc
import sys

import machine
import uasyncio as asyncio
import ubinascii as binascii
import uhashlib as hashlib
import uos as os
import utime
from micropython import const

sys.modules.clear()

gc.collect()


_CONNECTION_TIMEOUT = const(30)
_OTA_TIMEOUT = const(60)
_PORT = const(8266)
_CHUNK_SIZE = const(512)
_BUFFER = bytearray(_CHUNK_SIZE)
_FILE_TYPE = const(0x8000)


def reset(reason):
    for no in range(3, 0, -1):
        print('%i Reset because: %s' % (no, reason))
        utime.sleep(1)
    machine.reset()
    utime.sleep(1)
    sys.exit(-1)


class Timeout:
    def __init__(self, reason, timeout_sec):
        self.reason = reason
        self.satisfied = False
        self.timer = machine.Timer(-1)
        self.timer.init(
            period=timeout_sec * 1000,
            mode=machine.Timer.PERIODIC,
            callback=self._timer_callback
        )

    def _timer_callback(self, timer):
        gc.collect()
        if not self.satisfied:
            reset(self.reason)

    def deinit(self):
        self.timer.deinit()


class OtaUpdate:
    def __init__(self):
        self.timeout = None  # Will be set in run() and __call__()

    def run(self):
        gc.collect()

        loop = asyncio.get_event_loop()
        loop.create_task(asyncio.start_server(self, '0.0.0.0', _PORT))

        print('Wait %i sec for OTA connection on port %i' % (_CONNECTION_TIMEOUT, _PORT))
        self.timeout = Timeout(reason='no connection', timeout_sec=_CONNECTION_TIMEOUT)

        try:
            loop.run_forever()
        except Exception as e:
            sys.print_exception(e)
        except SystemExit as e:
            if e.args[0] == 0:
                reset('OTA Update complete successfully!')
            reset('Unknown sys exit code.')
        reset('OTA unknown error')

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
        self.timeout.deinit()
        gc.collect()
        self.timeout = Timeout(reason='OTA timeout', timeout_sec=_OTA_TIMEOUT)
        address = writer.get_extra_info('peername')
        print('Accepted connection from %s:%s' % address)
        while True:
            command = await self.read_line_string(reader)
            print('Receive command:', command)

            gc.collect()
            try:
                await getattr(self, 'command_%s' % command)(reader, writer)
            except AttributeError:
                await self.error(writer, 'Command unknown')
            except Exception as e:
                sys.print_exception(e)
                await self.error(writer, 'Command error')

    async def command_send_ok(self, reader, writer):
        await self.write_line_string(writer, 'OK')

    async def command_exit(self, reader, writer):
        await self.command_send_ok(reader, writer)
        self.timeout.deinit()
        utime.sleep(1)  # Don't close connection before server processed 'OK'
        sys.exit(0)

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
                print('Compare written file content', end=' ')
                sha256 = hashlib.sha256()
                with open(temp_file_name, 'rb') as f:
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
                    try:
                        os.remove(file_name)
                    except OSError:
                        pass  # e.g.: new file that doesn't exist, yet.

                    os.rename(temp_file_name, file_name)

                    if file_name.endswith('.mpy'):
                        py_filename = '%s.py' % file_name.rsplit('.', 1)[0]
                        try:
                            os.remove(py_filename)
                        except OSError:
                            pass  # *.py file doesn't exists

                    await self.command_send_ok(reader, writer)
                    return

            await self.error(writer, 'Hash error: %s' % hexdigest)
        finally:
            print('Remove temp file')
            try:
                os.remove(temp_file_name)
            except OSError:
                pass


if __name__ == '__main__':
    OtaUpdate().run()
