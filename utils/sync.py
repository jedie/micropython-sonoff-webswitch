import binascii
import hashlib
import json
import time
from json import JSONDecodeError
from pprint import pprint

import serial
from mpycntrl import MPyControl


class MyControl(MPyControl):
    def cmd_files_info(self, path="."):
        cmd = f"""
            import uos, json, uhashlib, ubinascii
            data={{}}
            chunk_size = const(512)
            buffer = bytearray(chunk_size)
            for name, file_type, inode, size in uos.ilistdir('{path}'):
                if file_type != 0x8000:
                    # Skip non files
                    continue

                sha256 = uhashlib.sha256()
                with open(name, 'rb') as f:
                    while True:
                        count = f.readinto(buffer, chunk_size)
                        if count < chunk_size:
                            sha256.update(buffer[:count])
                            break
                        else:
                            sha256.update(buffer)

                data[name]=(size, ubinascii.hexlify(sha256.digest()))

            print( json.dumps( data ) )
            """
        r = self.sendcmd(cmd)
        if len(r) == 0:
            raise Exception("timeout during execution")
        try:
            files = json.loads(r[0].decode())
        except JSONDecodeError as err:
            print('_'*80)
            print('Error: %s' % err)
            print('Raw output:')
            print(r)
            raise
        return files


class SyncToDevice:
    send_file_timeout = 1

    def __init__(self, src_path, verbose=False):
        self.src_path = src_path.resolve()
        self.verbose = verbose

        if self.verbose:
            print('Verbose mode activated.')

        assert self.src_path.is_dir(), 'Directory not found: %s' % self.src_path

        self.files_info = None  # Requested in self.update_device()

    def update_device(self):
        port = '/dev/ttyUSB0'
        baud = 115200
        bytesize = 8
        parity = 'N'
        stopbits = 1
        timeout = 0.35

        with serial.Serial(port=port, baudrate=baud,
                           bytesize=bytesize, parity=parity, stopbits=stopbits,
                           timeout=timeout) as ser:

            mpyc = MyControl(ser, debug=self.verbose, trace=False)

            # enter raw-repl mode
            r = mpyc.send_cntrl_c()
            print("received", r)

            pprint(mpyc.send_collect_ids())

            print('get device file informations...')
            print('-' * 100)
            self.files_info = mpyc.cmd_files_info()
            pprint(self.files_info)
            print('-' * 100)

            file_count = 0
            updated = []
            up2date = 0
            for item in self.src_path.iterdir():
                if item.is_dir():
                    print(f'Directories not supported, skip: %s' % item)
                    continue
                elif not item.is_file():
                    print(f'Skip not file: %s' % item)
                    continue

                file_count += 1
                print(item.name, end=' ', flush=True)

                if not self.client_file_outdated(item):
                    # local <-> device file are the same -> skip
                    up2date += 1
                    continue

                with item.open('rb') as f:
                    with mpyc.timeout(timeout=self.send_file_timeout):
                        mpyc.cmd_put(fnam=item.name, content=f.read())
                print('-' * 100)
                updated.append(item)

            print('*' * 100)
            print(f'*** Device update done:')
            print(f'*** {file_count} files')
            print(f'*** {up2date} files are up-to-date on device')
            print(f'*** {len(updated)} files updated on device:')
            for item in updated:
                print(f'*** * {item.name}')

    def client_file_outdated(self, file_path):
        try:
            device_file_size, device_sha256 = self.files_info[file_path.name]
        except KeyError:
            print('\nFile does not exist on device -> upload file.')
            return True

        local_file_size = file_path.stat().st_size
        if device_file_size != local_file_size:
            print()
            print(f'Device file size..: {device_file_size} Bytes')
            print(f'Local file size...: {local_file_size} Bytes')
            print('File size not the same -> upload file.')
            return True

        with file_path.open('rb') as f:
            local_sha256 = hashlib.sha256(f.read()).hexdigest()

        if local_sha256 != device_sha256:
            print()
            print(f'Device file SHA256...: {device_sha256!r}')
            print(f'Local file SHA256....: {local_sha256!r}')
            print('File SHA256 hash not the same -> upload file.')
            return True

        print('Skip file: Size + SHA256 are same')
        return False

def sync(src_path, verbose):
    SyncToDevice(src_path, verbose=verbose).update_device()
