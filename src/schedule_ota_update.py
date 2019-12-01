import gc
import sys

import machine
import utime as time
from rtc_memory import rtc_memory


def main():
    print('Schedule OTA via RTC RAM')
    gc.collect()
    rtc_memory.save(data={'run': 'ota-update'})  # Save to RTC RAM for next boot
    print('Hard reset device...')
    time.sleep(1)
    machine.reset()
    time.sleep(1)
    sys.exit()


if __name__ == '__main__':
    main()
