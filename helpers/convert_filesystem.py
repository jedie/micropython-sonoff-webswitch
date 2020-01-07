#
# !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
# !!! WARNING: Running this script may reformat the filesystem
# !!! WARNING: So take a backup first ;)
# !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
#
import esp
import flashbdev
import uos

FS_FAT = 'FAT'
FS_LITTLEFS = 'LittleFS'

uname = uos.uname()

print(uname.machine, uname.release)
print('MicroPython', uname.version)
print()

print('flashbdev.size....:', flashbdev.size)
print('reserved sectors..:', flashbdev.bdev.RESERVED_SECS)
print('start sector......: 0x%x' % flashbdev.bdev.START_SEC)
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
    buf = bytearray(16)
    flashbdev.bdev.readblocks(0, buf)
    if buf[3:8] == b'MSDOS':
        return FS_FAT
    elif buf[8:16] == b'littlefs':
        return FS_LITTLEFS
    return 'unknown'


def convert_filesystem2littlefs(force=False):
    filesystem_hex_dump(line_count=5, chunk_size=16)
    filesystem = detect_filesystem()
    print('Detected filesystem: %r' % filesystem)

    if force is True or filesystem != FS_LITTLEFS:
        print('Erase sector 0x%x' % flashbdev.bdev.START_SEC)
        esp.flash_erase(flashbdev.bdev.START_SEC)

        print('\nconvert to littlefs2...\n')  # only on ESP8266 and ESP32
        uos.VfsLfs2.mkfs(flashbdev.bdev)

        filesystem_hex_dump(line_count=5, chunk_size=16)
        print('Detected filesystem:', detect_filesystem())


if __name__ == '__main__':
    convert_filesystem2littlefs()
