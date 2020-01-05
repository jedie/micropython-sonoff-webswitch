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
