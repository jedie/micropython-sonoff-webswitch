import gc
import sys

import machine
import ujson as json


class Rtc:
    def __init__(self):
        self.rtc = machine.RTC()

        rtc = self.rtc.memory()  # Restore from RTC RAM
        if rtc:
            try:
                self.d = json.loads(rtc)
            except ValueError as e:
                sys.print_exception(e)
                print('RTC memory:', rtc)
                self.d = {}
        else:
            self.d = {}
        gc.collect()

    def save(self, data):
        self.d.update(data)
        self.rtc.memory(json.dumps(self.d))  # Save to RTC RAM
        gc.collect()

    def clear(self):
        self.rtc.memory(b'{}')
        self.d.clear()
        gc.collect()

    def incr_rtc_count(self, key):
        count = self.d.get(key, 0) + 1
        self.save(data={key: count})
        return count

    def isoformat(self, sep='T'):
        # e.g.: 2019-12-1T6:19:44+00:00
        dt = self.rtc.datetime()
        return '%i-%i-%i%s%i:%i:%i+00:00' % (dt[:3] + (sep,) + dt[3:6])

    def __str__(self):
        return '%r UTC: %s' % (self.d, self.isoformat())


if __name__ == '__main__':
    rtc = Rtc()
    print('RTC 1:', rtc)
    count = rtc.incr_rtc_count(key='test')
    print('RTC memory test call count:', count)
    print('RTC 2:', rtc)
