import sys

import utime as time


def ntp_sync(rtc):
    import ntptime

    print('Synchronize time from %r ...' % ntptime.host)
    print('old UTC:', rtc.isoformat())
    s = 1
    while True:
        try:
            ntptime.settime()
        except Exception as e:
            print('Error syncing time: %s, retry in %s sec.' % (e, s))
            time.sleep(s)
            s += 5
        else:
            print('new UTC:', rtc.isoformat())
            del ntptime
            del sys.modules['ntptime']
            return
