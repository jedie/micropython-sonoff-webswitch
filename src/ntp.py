import gc
import sys

import constants
import machine
import ntptime
import utime as time
from watchdog import watchdog

rtc = machine.RTC()


class NtpSync:
    error_count = 0
    success_count = 0
    last_refresh = None

    timer = machine.Timer(-1)

    def __init__(self):
        print('Sync NTP on init')
        self._sync()

        print('Start NTP period timer')
        self.timer.deinit()
        self.timer.init(
            period=constants.NTP_TIMER,
            mode=machine.Timer.PERIODIC,
            callback=self._timer_callback)

    def _timer_callback(self, timer):
        print('NTP timer callback for:', timer)
        try:
            self._sync()
        except Exception as e:
            sys.print_exception(e)
            self.timer.deinit()

    def _sync(self):
        print('Synchronize time from %r ...' % ntptime.host)
        gc.collect()
        print('old UTC:', rtc.datetime())
        s = 1
        while True:
            try:
                ntptime.settime()
            except Exception as e:
                print('Error syncing time: %s, retry in %s sec.' % (e, s))
                self.error_count += 1
                time.sleep(s)
                s += 5
            else:
                self.success_count += 1
                self.last_refresh = rtc.datetime()
                print('new UTC:', rtc.datetime())
                watchdog.feed()
                return

    def __str__(self):
        return 'NtpSync last refresh: %s - success count: %i - error count: %i' % (
            self.last_refresh, self.success_count, self.error_count
        )


ntp_sync = NtpSync()


if __name__ == '__main__':
    print(ntp_sync)
