

class Pin:
    OUT = 'out'
    IN = 'in'

    state = {}

    def __init__(self, no, in_out):
        self.no = no
        self.in_out = in_out

    def value(self, on_off=None):
        if on_off is None:
            return self.state[self.no]
        else:
            self.state[self.no] = on_off


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
    """
    http://docs.micropython.org/en/latest/esp8266/quickref.html#real-time-clock-rtc
    https://github.com/micropython/micropython/blob/master/lib/timeutils/timeutils.c
    https://github.com/micropython/micropython/blob/master/ports/esp8266/machine_rtc.c
    """

    __shared_state = {
        'rtc_memory': '',
        'time_tuple': (2000, 1, 1, 5, 0, 0, 0, 0)
    }

    def __init__(self):
        self.__dict__ = self.__shared_state

    def memory(self, data=None):
        if data is not None:
            self.__shared_state['rtc_memory'] = data

        return self.__shared_state['rtc_memory']

    def datetime(self, time_tuple=None):
        if time_tuple is not None:
            self.__shared_state['time_tuple'] = time_tuple

        return self.__shared_state['time_tuple']

    def deinit(self):
        self.__shared_state = {
            'rtc_memory': '',
            'time_tuple': (2000, 1, 1, 5, 0, 0, 0, 0)
        }
