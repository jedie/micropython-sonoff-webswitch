import sys

import utime as time
from rtc import rtc_isoformat


def ntp_sync():
    import ntptime

    print('Synchronize time from %r ...' % ntptime.host)
    print('old UTC:', rtc_isoformat())
    s = 1
    while True:
        try:
            ntptime.settime()
        except Exception as e:
            print('Error syncing time: %s, retry in %s sec.' % (e, s))
            time.sleep(s)
            s += 5
        else:
            print('new UTC:', rtc_isoformat())
            del ntptime
            del sys.modules['ntptime']
            return
