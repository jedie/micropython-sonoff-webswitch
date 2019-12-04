import gc
import sys

import machine
import utime as time
from rtc import Rtc

if __name__ == '__main__':
    print('Schedule OTA via RTC RAM')
    gc.collect()
    rtc = Rtc()
    rtc.save(data={'run': None})  # Save to RTC RAM for next boot
    print('Hard reset device...')
    time.sleep(1)
    machine.reset()
    time.sleep(1)
    sys.exit()
