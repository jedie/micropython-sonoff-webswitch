import gc

import machine
import ujson as json


class RtcMemory:
    def __init__(self):
        rtc_memory = machine.RTC().memory()  # Restore from RTC RAM
        if rtc_memory:
            self.rtc_memory = json.loads(rtc_memory)
        else:
            self.rtc_memory = {}
        gc.collect()

    def save(self, data):
        self.rtc_memory.update(data)
        machine.RTC().memory(json.dumps(self.rtc_memory))  # Save to RTC RAM
        gc.collect()

    def clear(self):
        machine.RTC().memory(b'{}')

    def incr_rtc_count(self, key):
        count = self.rtc_memory.get(key, 0) + 1
        self.save(data={key: count})
        return count

    def __str__(self):
        return str(self.rtc_memory)


if __name__ == '__main__':
    rtc_memory = RtcMemory()
    print('RTC Memory 1:', rtc_memory)
    count = rtc_memory.incr_rtc_count(key='test')
    print('RTC memory test call count:', count)
    print('RTC Memory 2:', rtc_memory)
