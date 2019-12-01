print('boot.py')   # noqa isort:skip

import gc

import esp
import micropython
import utime as time

for no in range(2, 0, -1):
    print('%i boot.py wait...' % no)
    time.sleep(1)

esp.osdebug(None)  # turn off vendor O/S debugging messages
esp.sleep_type(esp.SLEEP_NONE)  # Don't go into sleep mode

micropython.alloc_emergency_exception_buf(128)

gc.enable()
gc.collect()

print('boot.py END')
