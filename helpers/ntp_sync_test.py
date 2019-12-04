import sys

from rtc import Rtc

if __name__ == '__main__':
    print('sys.modules:', ', '.join(sys.modules.keys()))
    from ntp import ntp_sync

    ntp_sync(rtc=Rtc())  # update RTC via NTP
    del ntp_sync
    del sys.modules['ntp']

    print('sys.modules:', ', '.join(sys.modules.keys()))
