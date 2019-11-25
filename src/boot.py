import gc

import esp
import utime as time

print('gc.collect()')
gc.collect()


for no in range(2, 0, -1):
    print('%i boot.py wait...' % no)
    time.sleep(1)


print('Check Firmware:')
assert esp.check_fw() is True, "Firmware error?!?"
esp.osdebug(None)  # turn off vendor O/S debugging messages
esp.sleep_type(esp.SLEEP_NONE)  # Don't go into sleep mode


print('boot.py END')
