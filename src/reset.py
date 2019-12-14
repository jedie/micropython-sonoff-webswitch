import sys

import constants
import machine
import utime
from rtc import update_rtc_dict


class ResetDevice:
    def __init__(self, reason):
        print('Reset reason: %r' % reason)

        # Save reason in RTC RAM:
        update_rtc_dict(data={constants.RTC_KEY_RESET_REASON: reason})

    def reset(self):
        utime.sleep(1)
        machine.reset()
        utime.sleep(1)
        sys.exit()

    def schedule(self, period=2000):
        timer = machine.Timer(-1)
        timer.init(
            mode=machine.Timer.ONE_SHOT,
            period=period,
            callback=self.reset
        )
