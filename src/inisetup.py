"""
    based on origin:
        https://github.com/micropython/micropython/blob/master/ports/esp8266/modules/inisetup.py
"""
import esp
import flashbdev
import uos

FS_FAT = 'FAT'
FS_LITTLEFS = 'LittleFS'


def detect_filesystem():
    buf = bytearray(16)
    flashbdev.bdev.readblocks(0, buf)
    if buf[3:8] == b'MSDOS':
        return FS_FAT
    elif buf[8:16] == b'littlefs':
        return FS_LITTLEFS
    return 'unknown'


def setup():
    print("Performing initial setup")

    filesystem = detect_filesystem()
    print('Detected filesystem: %r' % filesystem)
    if filesystem != FS_LITTLEFS:
        print('Erase flash start sector 0x%x' % flashbdev.bdev.START_SEC)
        esp.flash_erase(flashbdev.bdev.START_SEC)

        print('convert to littlefs2')
        uos.VfsLfs2.mkfs(flashbdev.bdev)

    print('mount filesystem')
    vfs = uos.VfsLfs2(flashbdev.bdev)
    uos.mount(vfs, '/')

    with open("boot.py", "w") as f:
        f.write("""\
print('boot.py')   # noqa isort:skip
import gc
import sys

import esp
import micropython
import utime

for no in range(2, 0, -1):
    print('%i boot.py wait...' % no)
    utime.sleep(1)

esp.osdebug(None)  # turn off vendor O/S debugging messages
esp.sleep_type(esp.SLEEP_NONE)  # Don't go into sleep mode

micropython.alloc_emergency_exception_buf(128)

gc.enable()

# https://forum.micropython.org/viewtopic.php?f=2&t=7345&p=42390#p42390
gc.threshold(8192)

# default is:
#   sys.path=['', '/lib', '/']
# But we would like to be possible to overwrite frozen modues with .mpy on flash drive ;)
sys.path.insert(0, '.')
print('sys.path=%r' % sys.path)


print('boot.py END')
""")
    return vfs
