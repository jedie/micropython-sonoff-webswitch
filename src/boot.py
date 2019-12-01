import utime as time

for no in range(2, 0, -1):
    print('%i boot.py wait...' % no)
    time.sleep(1)

import esp
esp.osdebug(None)  # turn off vendor O/S debugging messages
esp.sleep_type(esp.SLEEP_NONE)  # Don't go into sleep mode

import micropython
micropython.alloc_emergency_exception_buf(128)

import gc
gc.enable()
gc.collect()

print('boot.py END')
