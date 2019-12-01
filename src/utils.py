import sys

import constants
import machine
import utime as time


class ResetDevice:
    def __init__(self, rtc, reason):
        print('Reset reason: %r' % reason)

        # Save reason in RTC RAM:
        rtc.save(data={constants.RTC_KEY_RESET_REASON: reason})

    def reset(self):
        time.sleep(1)
        machine.reset()
        time.sleep(1)
        sys.exit()

    def schedule(self, period=2000):
        timer = machine.Timer(-1)
        timer.init(
            mode=machine.Timer.ONE_SHOT,
            period=period,
            callback=self.reset
        )
