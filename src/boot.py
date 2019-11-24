import gc

import esp
import utime as time


for no in range(3, 0, -1):
    print('%i boot.py wait...' % no)
    time.sleep(1)


print('Check Firmware:')
assert esp.check_fw() is True, "Firmware error?!?"
esp.osdebug(None)       # turn off vendor O/S debugging messages


print('gc.collect()')
gc.collect()


print('boot.py END')