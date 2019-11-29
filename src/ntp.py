import gc

import machine
import ntptime
import utime as time

rtc = machine.RTC()

PERIOD = const(15 * 60 * 1000)  # 15 min


class NtpSync:
    error_count = 0
    success_count = 0
    last_refresh = None
    _next_refresh = 0

    def sync(self):
        gc.collect()

        if time.time() < self._next_refresh:
            # Last sync wasn't too long ago -> do nothing
            return

        self._next_refresh = time.time() + PERIOD

        print('Synchronize time from %r ...' % ntptime.host)
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
                gc.collect()
                return

    def __str__(self):
        return 'NtpSync last refresh: %s - success count: %i - error count: %i' % (
            self.last_refresh, self.success_count, self.error_count
        )


ntp_sync = NtpSync()


if __name__ == '__main__':
    print(ntp_sync)
