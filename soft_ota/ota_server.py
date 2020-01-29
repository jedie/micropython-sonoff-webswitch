"""
    soft-OTA Server
    ~~~~~~~~~~~~~~~
    Answering requests from devices micropython devices,
    to update all files on device.

    This OTA Server must be run on a host machine and
    not on the micropython device!
"""
import asyncio
import hashlib
import os
import socket
import time
from pathlib import Path

from soft_ota import mpy_cross
from utils import constants

SOCKET_TIMEOUT = 10

DNS_SERVER = '8.8.8.8'  # Google DNS Server ot get own IP
ENCODING = 'utf-8'


def get_ip_address():
    """
    :return: IP address of the host running this script.
    """
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.settimeout(SOCKET_TIMEOUT)
    s.connect((DNS_SERVER, 80))
    ip = s.getsockname()[0]
    s.close()
    return ip


class CommunicationError(RuntimeError):
    pass


def ip_range_iterator(own_ip, exclude_own):
    ip_prefix, own_no = own_ip.rsplit('.', 1)
    print(f'Scan:.....: {ip_prefix}.X')

    own_no = int(own_no)

    for no in range(1, 255):
        if exclude_own and no == own_no:
            continue

        yield f'{ip_prefix}.{no}'


class OtaStreamWriter(asyncio.StreamWriter):
    encoding = 'utf-8'

    async def write_text_line(self, text):
        self.write(b'%s\n' % text.encode('utf-8'))
        await self.drain()

    async def sendall(self, data):
        self.write(data)
        await self.drain()


async def open_connection(host=None, port=None):
    """A wrapper for create_connection() returning a (reader, writer) pair.

    Similar as asyncio.open_connection() but we use own OtaStreamWriter()
    """
    loop = asyncio.get_event_loop()
    reader = asyncio.StreamReader(limit=2 ** 16, loop=loop)
    protocol = asyncio.StreamReaderProtocol(reader, loop=loop)
    transport, _ = await loop.create_connection(lambda: protocol, host, port)
    writer = OtaStreamWriter(transport, protocol, reader, loop)
    return reader, writer


class SoftOtaServer:
    def __init__(self, verbose=False):
        self.verbose = verbose

        if self.verbose:
            print('Verbose mode activated.')

        assert constants.SRC_PATH.is_dir(), 'Directory not found: %s' % constants.SRC_PATH
        assert constants.BDIST_PATH.is_dir(), 'Directory not found: %s' % constants.BDIST_PATH

        self.own_ip = get_ip_address()
        print(f'Own IP....: {self.own_ip}')

        self.client_socket = None  # Client socked, created in self.run()
        self.client_chunk_size = None  # Change by client on connection in self.run()
        self.frozen_info = None  # Requested in self.update_device()
        self.flash_info = None  # Requested in self.update_device()

    async def update_device(self, reader, writer):
        peername = writer.get_extra_info('peername')
        print(f'Send Updates to {peername[0]}:{peername[1]}')

        await self.request_ping(reader, writer)

        self.client_chunk_size = await self.get_client_chunk_size(reader, writer)

        print('-' * 100)
        self.frozen_info = await self.request_frozen_info(reader, writer)
        print('-' * 100)
        self.flash_info = await self.request_flash_info(reader, writer)
        print('-' * 100)

        await self.check_micropython_version(reader, writer)

        file_count = 0
        updated = []
        up2date = 0
        for item in constants.BDIST_PATH.iterdir():
            if item.is_dir():
                print(f'Directories not supported, skip: %s' % item)
                continue
            elif not item.is_file():
                print(f'Skip not a file: %s' % item)
                continue

            file_count += 1
            print(item.name)

            if not self.client_file_outdated(item):
                # local <-> device file are the same -> skip
                up2date += 1
                continue

            await self.send_file(item, reader, writer)
            print('-' * 100)
            updated.append(item)

        await self.request_exit(reader, writer)
        print('*' * 100)
        print(f'*** Device {peername[0]}:{peername[1]} update done:')
        print(f'*** {file_count} files')
        print(f'*** {up2date} files are up-to-date on device')
        print(f'*** {len(updated)} files updated on device:')
        for item in updated:
            print(f'*** * {item.name}')

    async def receive_all(self, reader):
        if self.verbose:
            print('receive...', end='', flush=True)
        data = b''
        while True:
            chunk = await reader.read(1024)
            if self.verbose:
                print(chunk, end='', flush=True)
            if not chunk:
                break
            data += chunk
            if data.endswith(b'\n\n'):
                break

        if self.verbose:
            print()
        data = data.decode(ENCODING)
        data = data[:-2]  # remove last '\n\n' terminator
        return data

    async def readline(self, reader):
        if self.verbose:
            print('receive line...', end='', flush=True)

        line = await reader.readline()
        if self.verbose:
            print(line.decode(ENCODING, errors='replace'), flush=True)

        line = line.decode(ENCODING)
        line = line[:-1]  # remove last '\n' terminator
        return line

    async def wait_for_ok(self, reader, error_text):
        ok = await self.readline(reader)
        if ok != 'OK':
            raise CommunicationError(f'{error_text}: {ok!r}')

    async def request_ping(self, reader, writer):
        await writer.write_text_line('send_ok')
        await self.wait_for_ok(reader, error_text='Wrong ping response')

    async def get_client_chunk_size(self, reader, writer):
        await writer.write_text_line('chunk_size')
        client_chunk_size = await reader.readline()
        print(repr(client_chunk_size))
        client_chunk_size = int(client_chunk_size)
        print(f'Client chunk size: {client_chunk_size!r} Bytes')
        return client_chunk_size

    async def check_micropython_version(self, reader, writer):
        """
        Request sys.implementation.mpy from device and compare is with mpy_cross version
        See: https://forum.micropython.org/viewtopic.php?f=2&t=7506
        """
        print('\nCheck micropython versions:')
        mpy_cross_version = mpy_cross.version()

        await writer.write_text_line('mpy_version')
        raw_mpy_version = await reader.readline()
        sys_mpy = int(raw_mpy_version.decode('ASCII').strip())

        # sys.implementation.mpy & 0xff
        device_mpy_version = sys_mpy & 0xff

        print(f'mpv version on device is: v{device_mpy_version}')

        if device_mpy_version != mpy_cross_version:
            await self.request_exit(reader, writer)
            raise AssertionError(
                f'Version error!'
                f' Device mpy version does not match with installed mpy_cross!'
                f' ({device_mpy_version!r} != {mpy_cross_version!r}'
            )

        print('Version matched, ok.\n')

    async def request_device_info(self, reader, writer, info_type):
        print(f'Request "{info_type}" from device:')

        await writer.write_text_line(info_type)
        data = await self.receive_all(reader)
        data = data.rstrip('\r\n')

        info = {}
        for file_info in data.split('\r\n'):
            try:
                name, size, hash = file_info.split('\r')
            except ValueError:
                # e.g.: Device is completely empty
                print(f'Error in file info: {file_info!r}')
                print('Skip.')
            else:
                size = int(size)
                print(f'{name:25s} {size:4} Bytes - SHA256: {hash}')
                info[name] = (size, hash)
        return info

    async def request_frozen_info(self, reader, writer):
        """
        Request information about own frozen modules.
        """
        return await self.request_device_info(reader, writer, info_type='frozen_info')

    async def request_flash_info(self, reader, writer):
        """
        Request information about files stored in flash filesystem
        """
        return await self.request_device_info(reader, writer, info_type='flash_info')

    def client_file_outdated(self, file_path):
        try:
            device_file_size, device_sha256 = self.flash_info[file_path.name]
        except KeyError:
            print('\tFile does not exist on flash filesystem.')
            if file_path.suffix == '.mpy':
                # We must compare the ./src/*.py file with self.frozen_info ;)
                file_path = Path(constants.SRC_PATH, file_path.with_suffix('.py').name)

            try:
                device_file_size, device_sha256 = self.frozen_info[file_path.name]
            except KeyError:
                print('\tFile does also not exist as frozen modules -> upload file.')
                return True

        # compare file size

        local_file_size = file_path.stat().st_size
        if device_file_size != local_file_size:
            print()
            print(f'\tDevice file size..: {device_file_size} Bytes')
            print(f'\tLocal file size...: {local_file_size} Bytes')
            print('\tFile size not the same -> upload file.')
            return True

        # compare SHA256 hash

        with file_path.open('rb') as f:
            local_sha256 = hashlib.sha256(f.read()).hexdigest()
        if local_sha256 != device_sha256:
            print()
            print(f'\tDevice file SHA256...: {device_sha256!r}')
            print(f'\tLocal file SHA256....: {local_sha256!r}')
            print('\tFile SHA256 hash not the same -> upload file.')
            return True

        print('\tSkip file: Size + SHA256 are same')
        return False

    async def send_file(self, file_path, reader, writer):
        """
        Send file to micropython device
        """
        file_size = file_path.stat().st_size
        print(f' *** send {file_path}', end=' ')

        await writer.write_text_line('receive_file')
        await writer.write_text_line(file_path.name)
        await writer.write_text_line(str(file_size))
        with file_path.open('rb') as f:
            sha256 = hashlib.sha256(f.read()).hexdigest()
            f.seek(0)

            print('SHA256:', sha256)
            await writer.write_text_line(sha256)

            await self.wait_for_ok(reader, error_text='No OK after file info')

            print(f'send ({file_size}Bytes)', end='', flush=True)
            while True:
                data = f.read(self.client_chunk_size)
                if not data:
                    break
                print('.', end='', flush=True)
                await writer.sendall(data)

        print('Send file, completed.')
        await self.wait_for_ok(reader, error_text='No OK after file send')

    async def request_exit(self, reader, writer):
        await writer.write_text_line('exit')
        await self.wait_for_ok(reader, error_text='Wrong exit response')

    async def port_scan_and_serve(self, port):
        print()
        ips = tuple(ip_range_iterator(self.own_ip, exclude_own=True))

        print(f'Wait vor devices on port: {port}', end=' ', flush=True)
        clients = []
        while True:
            connections = [
                asyncio.wait_for(open_connection(ip, port), timeout=0.5)
                for ip in ips
            ]
            results = await asyncio.gather(*connections, return_exceptions=True)
            for ip, result in zip(ips, results):
                if isinstance(result, asyncio.TimeoutError):
                    continue
                elif not isinstance(result, tuple):
                    continue

                print('Connected to:', ip)
                try:
                    await self.update_device(*result)
                except ConnectionResetError as e:
                    print(e)
                    continue
                clients.append(ip)

            if clients:
                return clients

            print('.', end='', flush=True)
            if os.environ.get('OTA_NO_LOOP') is not None:
                # Used in unittests, see: tests/test_soft_ota_server.py
                print('Exit after one try, because OTA_NO_LOOP is set, ok.')
                return clients
            time.sleep(2)

    def run(self, port):
        loop = asyncio.get_event_loop()
        return loop.run_until_complete(
            self.port_scan_and_serve(port=port)
        )
