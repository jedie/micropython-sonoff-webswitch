

class Pin:
    OUT = 'out'
    IN = 'in'

    def __init__(self, no, in_out):
        self.no = no
        self.in_out = in_out


class Timer:
    ONE_SHOT = 'one shot'

    def __init__(self, id):
        self.id = id

    def init(self, period, mode, callback):
        self.period = period
        self.mode = mode
        self.callback = callback

    def deinit(self):
        pass


class RTC:
    _memory = ''

    def __init__(self):
        pass

    def memory(self):
        return self._memory

    def datetime(self):
        return (2019, 5, 1, 4, 13, 12, 11, 0)
