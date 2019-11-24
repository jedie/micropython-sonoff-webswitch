import gc
import sys

import constants
import machine
import utime as time

rtc = machine.RTC()


class Watchdog:
    last_feed = time.time()
    last_refresh = None
    timer_count = 0
    feed_count = 0

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
        print('Watchdog timer callback...', end='')
        gc.collect()
        self.timer_count += 1
        self.last_refresh = rtc.datetime()
        print('diff:', self.last_diff)
        if self.last_diff >= self.timeout:
            for no in range(3, 0, -1):
                print('Watchdog timeout -> reset in %i sec...' % no)
                time.sleep(1)

            self.timer.deinit()
            machine.reset()  # Hard reset
            sys.exit()  # Soft reset
        print(self)

    def feed(self):
        print('Watchdog feeded:', self)
        self.last_feed = time.time()
        self.feed_count += 1

    def deinit(self):
        self.timer.deinit()

    def __repr__(self):
        return (
            '<Watchdog timeout: %s'
            ' - last diff: %s'
            ' - last refresh: %s'
            ' - timer count: %s'
            ' - feed count: %s'
        ) % (
            self.timeout, self.last_diff, self.last_refresh, self.timer_count, self.feed_count
        )


watchdog = Watchdog()


def test(watchdog):
    print('test start...')
    watchdog.deinit()  # deinit global watchdog

    # Create new one with shorter timeout:
    watchdog = Watchdog(
        check_period=3 * 1000,  # 2 sec
        timeout=2 * 1000,  # 1 sec
    )  
    print(watchdog)
    for _ in range(10):
        print('.', end='')
        time.sleep(0.5)
        watchdog.feed()
    print('\nfeed end\n')

    print(watchdog)

    while True:
        print(watchdog)
        time.sleep(0.5)


if __name__ == '__main__':
    test(watchdog)  # will reset the device !
    print('test end.')  # should never happen
