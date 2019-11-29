import gc

import machine
import ujson as json


class RtcMemory:
    def __init__(self):
        rtc_memory = machine.RTC().memory()  # Restore from RTC RAM
        if rtc_memory:
            self.d = json.loads(rtc_memory)
        else:
            self.d = {}
        gc.collect()

    def save(self, data):
        self.d.update(data)
        machine.RTC().memory(json.dumps(self.d))  # Save to RTC RAM
        gc.collect()

    def clear(self):
        machine.RTC().memory(b'{}')
        self.d.clear()
        gc.collect()

    def incr_rtc_count(self, key):
        count = self.d.get(key, 0) + 1
        self.save(data={key: count})
        return count

    def __str__(self):
        return str(self.d)


rtc_memory = RtcMemory()

if __name__ == '__main__':
    print('RTC Memory 1:', rtc_memory)
    count = rtc_memory.incr_rtc_count(key='test')
    print('RTC memory test call count:', count)
    print('RTC Memory 2:', rtc_memory)
