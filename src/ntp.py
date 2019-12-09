import sys

import utime as time
from rtc import rtc_isoformat


def ntp_sync():
    import ntptime

    print('Synchronize time from %r ...' % ntptime.host)
    print('old UTC:', rtc_isoformat())
    for s in range(5):
        try:
            ntptime.settime()
        except Exception as e:
            print('Error syncing time: %s, retry in %s sec.' % (e, s * 5))
            time.sleep(s * 5)
        else:
            print('new UTC:', rtc_isoformat())
            del ntptime
            del sys.modules['ntptime']
            return True

    from reset import ResetDevice
    ResetDevice(reason='Failed NTP sync').reset()
