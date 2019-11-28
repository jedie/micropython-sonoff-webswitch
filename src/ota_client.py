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
import ubinascii as binascii
import uhashlib as hashlib
import uos as os
import usocket as socket
import utime as time

SOCKET_TIMEOUT = const(10)
PORT = const(8266)
CHUNK_SIZE = const(1024)
ENCODING = 'utf-8'


def reset():
    for no in range(3, 1, -1):
        print('Hard reset device in %i sec...' % no)
        time.sleep(1)
    machine.reset()
    time.sleep(1)
    sys.exit()


class OtaClient:
    def __init__(self, server_socket):
        self.server_socket = server_socket

    def run(self):
        self.server_socket.settimeout(SOCKET_TIMEOUT)

        commands = {
            'send_ok': self.send_ok,
            'chunk_size': self.chunk_size,
            'file_info': self.file_info,
            'receive_file': self.receive_file,
        }

        while True:
            print('\nwait for command...', end='')
            command = self.read_line_string()
            if not command:
                print('Get empty command: Abort.')
                break

            print('Receive command:', command)
            if command == 'exit':
                print('exit!')
                self.send_ok()
                break

            gc.collect()

            try:
                commands[command]()
            except KeyError:
                print('Command unknown!')
            except Exception as e:
                print('Error running command:')
                sys.print_exception(e)

            print('Send new line: Command ends.')
            self.server_socket.sendall(b'\n')

            gc.collect()

        return 'OK'

    def read_line_bytes(self):
        gc.collect()
        line_bytes = self.server_socket.readline()
        if not line_bytes:
            return b''
        if not line_bytes.endswith(b'\n'):
            raise AssertionError('Byte line not terminated:', repr(line_bytes))
        return line_bytes[:-1]

    def read_line_string(self):
        return self.read_line_bytes().decode(ENCODING)

    def send_ok(self, terminated=False):
        self.server_socket.sendall(b'OK')
        if terminated:
            self.server_socket.sendall(b'\n')

    def file_info(self):
        """
        Send file size, SHA256 from local filesystem to server,
        """
        print('file info for:', end=' ')
        file_name = self.read_line_string()
        print(file_name)
        try:
            stat = os.stat(file_name)
        except OSError:
            self.server_socket.sendall(b'File not found!')
            return
        self.send_ok(terminated=True)
        self.server_socket.sendall(b','.join([b'%i' % no for no in stat]))
        self.server_socket.sendall(b'\n')
        sha256 = hashlib.sha256()
        with open(file_name, "rb") as f:
            sha256.update(f.read(CHUNK_SIZE))
        sha256 = binascii.hexlify(sha256.digest())
        print('SHA256:', sha256)
        self.server_socket.sendall(sha256)

    def chunk_size(self):
        """
        Send our chunk size in bytes.
        """
        self.server_socket.sendall(b'%i' % CHUNK_SIZE)

    def receive_file(self):
        """
        Store a new/updated file on local micropython device.
        """
        print('receive file', end=' ')
        file_name = self.read_line_string()
        print(file_name)
        file_size = int(self.read_line_string())
        print('%i Bytes' % file_size)
        file_sha256 = self.read_line_string()
        print('SHA256: %r' % file_sha256)
        self.send_ok(terminated=True)

        temp_file_name = '%s.temp' % file_name
        print('Create %s' % temp_file_name)
        try:
            with open(temp_file_name, 'wb') as f:
                print('receive data', end='')
                sha256 = hashlib.sha256()
                received = 0
                while True:
                    data = self.server_socket.recv(CHUNK_SIZE)
                    if not data:
                        break

                    print('.', end='')

                    f.write(data)
                    sha256.update(data)

                    received += len(data)
                    if received >= file_size:
                        print('completed')
                        break

            print('Received %i Bytes' % received, end=' ')

            local_file_size = os.stat(temp_file_name)[6]
            print('Written %i Bytes' % local_file_size)
            if local_file_size != file_size:
                print('Size error!')
                self.server_socket.sendall(b'Size error!\n')
                raise AssertionError('Size error!')

            hexdigest = binascii.hexlify(sha256.digest()).decode(ENCODING)
            if hexdigest == file_sha256:
                print('Hash OK:', hexdigest)
                print('Replace old file.')
                try:
                    os.remove(file_name)
                except OSError:
                    pass  # e.g.: new file that doesn't exist, yet.

                os.rename(temp_file_name, file_name)

                print('Compare written file content...')
                sha256 = hashlib.sha256()
                with open(file_name, 'rb') as f:
                    while True:
                        data = f.read(CHUNK_SIZE)
                        if not data:
                            break
                        sha256.update(data)

                hexdigest = binascii.hexlify(sha256.digest()).decode(ENCODING)
                if hexdigest == file_sha256:
                    print('Hash OK:', hexdigest)
                    self.send_ok()
                    return

            print('Hash Error:', hexdigest)
            self.server_socket.sendall(b'Hash error!\n')
            raise AssertionError('Hash error!')
        finally:
            print('Remove temp file')
            try:
                os.remove(temp_file_name)
            except OSError:
                pass


def get_active_wlan():
    for interface_type in (network.AP_IF, network.STA_IF):
        wlan = network.WLAN(interface_type)
        if wlan.active():
            return wlan
    raise RuntimeError('WiFi not active!')


def discovery_ota_server():
    gc.collect()
    own_ip = get_active_wlan().ifconfig()[0]
    print('Own IP:', own_ip)
    ip_prefix = own_ip.rsplit('.', 1)[0]

    for timeout in (0.15, 0.3, 0.5):
        print('\nScan: %s.X with timeout: %s' % (ip_prefix, timeout), end='')
        for no in range(1, 255):
            gc.collect()
            server_address = ('%s.%i' % (ip_prefix, no), PORT)
            print('.', end='')

            sock = socket.socket()
            sock.settimeout(timeout)
            try:
                sock.connect(server_address)
            except OSError:
                sock.close()
            else:
                print('\nFound OTA Server at: %s:%s' % server_address)
                return sock

    raise RuntimeError('OTA Server not found!')


def do_ota_update():
    server_socket = discovery_ota_server()
    gc.collect()
    try:
        return OtaClient(server_socket).run()
    except Exception as e:
        sys.print_exception(e)
        reset()
    finally:
        server_socket.close()


if __name__ == '__main__':
    print(do_ota_update())
    reset()
