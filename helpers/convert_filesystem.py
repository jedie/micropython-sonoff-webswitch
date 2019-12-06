#
# !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
# !!! WARNING: Running this script will reformat the filesystem
# !!! WARNING: So take a backup first ;)
# !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
#

import flashbdev
import uos as os

uname = os.uname()

print(uname.machine, uname.release)
print('MicroPython', uname.version)
print()

print('flashbdev.size....:', flashbdev.size)
print('reserved sectors..:', flashbdev.bdev.RESERVED_SECS)
print('start sector......:', flashbdev.bdev.START_SEC)
print('sector size.......:', flashbdev.bdev.SEC_SIZE)
print('num blocks........:', flashbdev.bdev.NUM_BLK)


def filesystem_hex_dump(line_count=10, chunk_size=16):
    buf = bytearray(chunk_size)
    for block_num in range(line_count):
        offset = block_num * chunk_size
        print('%04x - %04x' % (offset, offset + chunk_size - 1), end=' - ')
        flashbdev.bdev.readblocks(block_num, buf)
        print(' '.join('%02x' % char for char in buf), end=' - ')
        print(''.join(chr(char) if 32 < char < 177 else '.' for char in buf))


def detect_filesystem():
    buf = bytearray(8)
    flashbdev.bdev.readblocks(0, buf)
    if buf[3:8] == b'MSDOS':
        return 'FAT'
    return 'unknown'


filesystem_hex_dump(line_count=5, chunk_size=16)
print('Detected filesystem:', detect_filesystem())

print('\nconvert to FAT...\n')  # only on ESP8266 and ESP32

# os.umount('/')
os.VfsFat.mkfs(flashbdev.bdev)
# os.mount(flashbdev.bdev, '/')

filesystem_hex_dump(line_count=5, chunk_size=16)
print('Detected filesystem:', detect_filesystem())

print('\nconvert to littlefs2...\n')  # only on ESP8266 and ESP32

# os.umount('/')
# os.VfsLfs.mkfs(flashbdev.bdev)  # AttributeError: 'module' object has no attribute 'VfsLfs'
os.VfsLfs2.mkfs(flashbdev.bdev)  # AttributeError: 'module' object has no attribute 'VfsLfs2'
# os.mount(flashbdev.bdev, '/')

filesystem_hex_dump(line_count=5, chunk_size=16)
print('Detected filesystem:', detect_filesystem())
