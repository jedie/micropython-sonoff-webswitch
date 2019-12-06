"""
    Force start web server.
    This is normally not needed, see main.py
"""

import gc
import sys

import machine
import utime as time
from rtc import update_rtc_dict

if __name__ == '__main__':
    print('Schedule web server start via RTC RAM')
    gc.collect()

    update_rtc_dict(data={'run': 'web-server'})  # Save to RTC RAM for next boot

    print('Hard reset device...')
    time.sleep(1)
    machine.reset()
    time.sleep(1)
    sys.exit()
