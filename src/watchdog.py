import gc

import constants
import machine
import utime


class Watchdog:
    last_feed = 0
    last_check = 0
    check_count = 0

    timer = machine.Timer(-1)

    def __init__(self, wifi, check_callback):
        self.wifi = wifi
        self.check_callback = check_callback

        print('Start Watchdog period timer')
        self.timer.deinit()
        self.timer.init(
            period=constants.WATCHDOG_CHECK_PERIOD,
            mode=machine.Timer.PERIODIC,
            callback=self._timer_callback
        )

    def _timer_callback(self, timer):
        from watchdog_checks import check
        check(last_feed=self.last_feed, wifi=self.wifi, check_callback=self.check_callback)
        del check
        gc.collect()

        self.check_count += 1

        from timezone import localtime_isoformat
        self.last_check = localtime_isoformat()

    def feed(self):
        self.last_feed = utime.time()

    def __str__(self):
        # get reset info form RTC RAM:
        from rtc import get_rtc_value
        reset_count = get_rtc_value(constants.RTC_KEY_WATCHDOG_COUNT, 0)
        reset_reason = get_rtc_value(constants.RTC_KEY_RESET_REASON)
        return (
            'last check: %s,'
            ' check count: %s,'
            ' feed since: %i,'
            ' reset count: %s,'
            ' last reset reason: %s'
        ) % (
            self.last_check, self.check_count,
            (utime.time() - self.last_feed),
            reset_count, reset_reason,
        )
