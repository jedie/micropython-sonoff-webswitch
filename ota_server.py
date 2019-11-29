"""
    OTA Server
    ~~~~~~~~~~
    Answering requests from devices micropython devices,
    to update all files on device.

    This OTA Server must be run on a host machine and
    not on the micropython device!
"""

import hashlib
import socket
import sys
import time
from pathlib import Path

SOCKET_TIMEOUT = 10
PORT = 8266
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


class OtaServer:
    def __init__(self, ip, src_path, verbose=False):
        self.ip = ip
        self.src_path = src_path.resolve()
        self.verbose = verbose

        if self.verbose:
            print('Verbose mode activated.')

        assert self.src_path.is_dir(), 'Directory not found: %s' % self.src_path

        self.client_socket = None  # Client socked, created in self.run()
        self.client_chunk_size = None  # Change by client on connection in self.run()

    def run(self):
        print(f'Start OTA server for: {self.src_path}')

        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
            server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            server_socket.bind((self.ip, PORT))
            server_socket.listen(1)
            while True:
                print('_' * 100)
                print(f'wait for connection on {self.ip}:{PORT}...')
                self.client_socket, addr = server_socket.accept()
                print('Request from:', addr)

                self.client_socket.settimeout(SOCKET_TIMEOUT)

                try:
                    self.do_ping()
                    self.client_chunk_size = self.get_client_chunk_size()

                    file_count = 0
                    updated = []
                    up2date = 0
                    for item in self.src_path.iterdir():
                        print('')
                        print('_' * 100)
                        if item.is_dir():
                            print(f'Directories not supported, skip: %s' % item)
                            continue
                        elif not item.is_file():
                            print(f'Skip not file: %s' % item)
                            continue

                        file_count += 1
                        print('Update file: %s' % item)

                        if not self.client_file_outdated(item):
                            # local <-> device file are the same -> skip
                            up2date += 1
                            continue

                        self.send_file(item)
                        updated.append(item)

                    self.send_exit()
                    print()
                    print(f'*** Device {addr} update done:')
                    print(f'*** {file_count} files')
                    print(f'*** {up2date} files are up-to-date on device')
                    print(f'*** {len(updated)} files updated on device:')
                    for item in updated:
                        print(f'*** * {item.name}')

                except ConnectionResetError as err:
                    print(err)
                finally:
                    self.client_socket.close()

    def client_file_outdated(self, file_path):
        try:
            device_file_size, device_sha256 = self.get_file_info(file_path=file_path)
        except FileNotFoundError:
            print('File does not exist on device -> upload file.')
            return True

        local_file_size = file_path.stat().st_size
        if device_file_size != local_file_size:
            print(f'Device file size..: {device_file_size} Bytes')
            print(f'Local file size...: {local_file_size} Bytes')
            print('File size not the same -> upload file.')
            return True

        print('File size the same: Check Hash.')

        with file_path.open('rb') as f:
            local_sha256 = hashlib.sha256(f.read()).hexdigest()

        if local_sha256 != device_sha256:
            print(f'Device file SHA256...: {device_sha256!r}')
            print(f'Local file SHA256....: {local_sha256!r}')
            print('File SHA256 hash not the same -> upload file.')
            return True

        print('File SHA256 the same -> skip upload file.')
        return False

    def send_line(self, line):
        if not isinstance(line, bytes):
            line = line.encode(ENCODING)

        line += b'\n'
        if self.verbose:
            print('\nsend:', repr(line))
        self.client_socket.sendall(line)

    def readline(self):
        if self.verbose:
            print('receive line...', end='', flush=True)
        line = b''
        while True:
            char = self.client_socket.recv(1)
            if self.verbose:
                print(char.decode(ENCODING, errors='replace'), end='', flush=True)
            if not char or char == b'\n':
                break
            line += char

        if self.verbose:
            print()
        return line.decode(ENCODING)

    def receive_all(self):
        if self.verbose:
            print('receive...', end='', flush=True)
        data = b''
        while True:
            chunk = self.client_socket.recv(1024)
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
        data = data.strip()
        return data

    def wait_for_ok(self, message='no OK received', raise_error=True):
        ok = self.readline()
        if ok != "OK":
            if raise_error:
                raise CommunicationError(message)
            return ok
        return True

    def do_ping(self):
        self.send_line('send_ok')
        self.wait_for_ok(message='Get no OK')

    def get_client_chunk_size(self):
        self.send_line('chunk_size')
        client_chunk_size = int(self.readline())
        print(f'Client chunk size: {client_chunk_size!r} Bytes')
        return client_chunk_size

    def request_filelist(self):
        print('request file list')
        self.send_line('filelist')
        content = self.receive_all()
        print(content)

    def send_exit(self):
        self.send_line('exit')
        self.wait_for_ok(message='No OK after exit!')

    def send_file(self, file_path):
        """
        Send file to micropython device
        """
        file_size = file_path.stat().st_size
        print(f'send {file_path.name} ({file_size}Bytes)')

        self.send_line('receive_file')
        self.send_line(file_path.name)
        self.send_line(str(file_size))
        with file_path.open('rb') as f:
            sha256 = hashlib.sha256(f.read()).hexdigest()
            f.seek(0)

            print('sha256:', sha256)
            self.send_line(sha256)

            self.wait_for_ok(message='No OK after file info!')

            while True:
                data = f.read(self.client_chunk_size)
                if not data:
                    break
                print(f'send {len(data)} Bytes...')
                self.client_socket.sendall(data)

        print('Send file, completed.')
        self.wait_for_ok(message='No OK after file send!')

    def get_file_info(self, file_path):
        """
        Request file size, SHA256 hash from micropython device
        """
        print(f'Request file info for: {file_path.name}...', end='')
        assert file_path.is_file(), 'File not found: %s' % file_path

        self.send_line('file_info')
        self.send_line(file_path.name)
        response = self.wait_for_ok(raise_error=False)
        if response is not True:
            raise FileNotFoundError

        stats = self.readline()
        stats = tuple([int(no) for no in stats.split(',')])
        # print('File stat:', stats)
        file_size = stats[6]
        print('File size: %i Bytes' % file_size)
        sha256 = self.readline()
        print('SHA256:', sha256)
        return file_size, sha256


if __name__ == '__main__':
    base_path = Path(__file__).parent
    server = OtaServer(
        ip=get_ip_address(),
        src_path=Path(base_path, 'src'),  # Put these files on micropython device
        verbose=False,
    )
    while True:
        print('Start Server (Abort with Control-C)')
        try:
            server.run()
        except (CommunicationError, socket.timeout) as err:
            print('Error:', err)
        except KeyboardInterrupt:
            sys.exit()

        for i in range(5, 1, -1):
            print(f'Restart server in {i} sec...')
            time.sleep(1)
