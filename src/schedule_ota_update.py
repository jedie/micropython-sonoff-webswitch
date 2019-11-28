import gc
import sys

import machine
import utime as time
from rtc_memory import RtcMemory


def main():
    print('Schedule OTA via RTC RAM')
    gc.collect()
    RtcMemory().save(data={'run': 'ota-update'})  # Save to RTC RAM for next boot
    print('Hard reset device...')
    machine.reset()
    time.sleep(1)
    sys.exit()


if __name__ == '__main__':
    main()
