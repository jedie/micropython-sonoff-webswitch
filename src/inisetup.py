"""
    based on origin:
        micropython/ports/esp8266/modules/inisetup.py
"""
import uos
from flashbdev import bdev


def check_bootsec():
    buf = bytearray(bdev.SEC_SIZE)
    bdev.readblocks(0, buf)
    empty = True
    for b in buf:
        if b != 0xff:
            empty = False
            break
    if empty:
        return True
    fs_corrupted()


def fs_corrupted():
    import time
    while True:
        print("""\
The FAT filesystem starting at sector %d with size %d sectors appears to
be corrupted. If you had important data there, you may want to make a flash
snapshot to try to recover it. Otherwise, perform factory reprogramming
of MicroPython firmware (completely erase flash, followed by firmware
programming).
""" % (bdev.START_SEC, bdev.blocks))
        time.sleep(3)


def setup():
    check_bootsec()
    print("Performing initial setup")
    uos.VfsLfs2.mkfs(bdev)
    vfs = uos.VfsLfs2(bdev)
    uos.mount(vfs, '/')
    with open("boot.py", "w") as f:
        f.write("""\
print('boot.py')   # noqa isort:skip
import gc

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

print('boot.py END')
""")
    return vfs
