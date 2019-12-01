import gc

import ntptime
import utime as time

_PERIOD = const(15 * 60 * 1000)  # 15 min


class NtpSync:
    error_count = 0
    success_count = 0
    last_refresh = None
    _next_refresh = 0

    def sync(self, rtc):
        gc.collect()

        if time.time() < self._next_refresh:
            # Last sync wasn't too long ago -> do nothing
            return

        self._next_refresh = time.time() + _PERIOD

        print('Synchronize time from %r ...' % ntptime.host)
        print('old UTC:', rtc.isoformat())
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
                self.last_refresh = rtc.isoformat()
                print('new UTC:', self.last_refresh)
                gc.collect()
                return

    def __str__(self):
        return 'NtpSync last refresh: %s - success count: %i - error count: %i' % (
            self.last_refresh, self.success_count, self.error_count
        )


if __name__ == '__main__':
    from rtc import Rtc
    ntp_sync = NtpSync()
    ntp_sync.sync(rtc=Rtc())
    print(ntp_sync)
