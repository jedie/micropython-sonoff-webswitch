import gc

import constants
import machine
import utime as time
from micropython import const
from rtc import get_rtc_value, rtc_isoformat

_CHECK_PERIOD = const(50 * 1000)  # 50 sec


class Watchdog:
    last_feed = 0
    last_check = 0
    check_count = 0

    timer = machine.Timer(-1)

    def __init__(self, wifi):
        self.wifi = wifi

        print('Start Watchdog period timer')
        self.timer.deinit()
        self.timer.init(
            period=_CHECK_PERIOD,
            mode=machine.Timer.PERIODIC,
            callback=self._timer_callback
        )

    def _timer_callback(self, timer):
        from watchdog_checks import check
        check(last_feed=self.last_feed, wifi=self.wifi)
        del check
        gc.collect()

        self.check_count += 1
        self.last_check = rtc_isoformat()

    def deinit(self):
        self.timer.deinit()

    def feed(self):
        self.last_feed = time.time()

    def __str__(self):
        # get reset info form RTC RAM:
        reset_count = get_rtc_value(constants.RTC_KEY_WATCHDOG_COUNT, 0)
        reset_reason = get_rtc_value(constants.RTC_KEY_RESET_REASON)
        return (
            'Watchdog -'
            ' last check: %s,'
            ' check count: %s,'
            ' feed since: %i,'
            ' reset count: %s,'
            ' last reset reason: %s'
        ) % (
            self.last_check, self.check_count,
            (time.time() - self.last_feed),
            reset_count, reset_reason,
        )
