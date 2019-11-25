import gc
import sys

import constants
import machine
import utime as time
from rtc_memory import RtcMemory

rtc = machine.RTC()


class Watchdog:
    last_feed = time.time()
    last_refresh = None
    timer_count = 0
    feed_count = 0
    reset_count = RtcMemory().rtc_memory.get('watchdog_reset', 0)

    timer = machine.Timer(-1)

    def __init__(self, check_period=None, timeout=None):
        self.check_period = check_period or constants.WATCHDOG_CHECK_PERIOD
        self.timeout = timeout or constants.WATCHDOG_TIMEOUT

        assert self.check_period > self.timeout

        print('Start Watchdog period timer')
        self.timer.deinit()
        self.timer.init(
            period=self.check_period,
            mode=machine.Timer.PERIODIC,
            callback=self._timer_callback)

    @property
    def last_diff(self):
        return (time.time() - self.last_feed) * 1000

    def _timer_callback(self, timer):
        gc.collect()
        self.timer_count += 1
        self.last_refresh = rtc.datetime()
        if self.last_diff >= self.timeout:
            for no in range(3, 0, -1):
                print('Watchdog timeout -> reset in %i sec...' % no)
                time.sleep(1)

            RtcMemory().incr_rtc_count(key='watchdog_reset')  # Save reset count
            self.timer.deinit()
            machine.reset()  # Hard reset
            sys.exit()  # Soft reset

    def feed(self):
        self.last_feed = time.time()
        self.feed_count += 1

    def deinit(self):
        self.timer.deinit()

    def __str__(self):
        return (
            'Watchdog timeout: %s,'
            ' last diff: %s,'
            ' last refresh: %s,'
            ' reset count: %s,'
            ' timer count: %s,'
            ' feed count: %s,'
        ) % (
            self.timeout, self.last_diff, self.last_refresh,
            self.reset_count, self.timer_count, self.feed_count
        )


watchdog = Watchdog()


if __name__ == '__main__':
    print(watchdog)
