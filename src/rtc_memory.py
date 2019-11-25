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

    def save(self):
        machine.RTC().memory(json.dumps(self.rtc_memory))
        gc.collect()

    def incr_rtc_count(self, key):
        count = self.rtc_memory.get(key, 0) + 1
        self.rtc_memory[key] = count
        self.save()
        return count


if __name__ == '__main__':
    count = RtcMemory().incr_rtc_count(key='test')
    print('RTC memory test call count:', count)
