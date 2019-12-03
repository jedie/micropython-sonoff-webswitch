import gc

import machine

_CHECK_PERIOD = const(20 * 1000)  # 20 sec


def parse_get_time(raw):
    if raw:
        hours, minutes = raw.split('%3A')
        hours = int(hours)
        minutes = int(minutes)
        return hours, minutes


def set_timer_from_web(rtc, get_parameters):
    rtc.save(data={
        'on': parse_get_time(get_parameters['on']),
        'off': parse_get_time(get_parameters['off']),
        'active': get_parameters['active'] == 'on'
    })


def get_timer_form_value(rtc, key):
    value = rtc.d.get(key)
    if not value:
        return ''
    return '%02i:%02i' % (value[0], value[1])


class AutomaticTimer:
    last_check = 0
    check_count = 0
    last_action = None

    timer = machine.Timer(-1)

    def __init__(self, rtc, pins):
        self.rtc = rtc
        self.pins = pins

        print('Start Automatic Timer')
        self.timer.deinit()
        self.timer.init(
            period=_CHECK_PERIOD,
            mode=machine.Timer.PERIODIC,
            callback=self._timer_callback
        )

    @property
    def on_time(self):
        return self.rtc.d.get('on')

    @property
    def off_time(self):
        return self.rtc.d.get('off')

    @property
    def active(self):
        return self.rtc.d.get('active', False)

    def _turn_on(self):
        self.pins.relay.on()
        self.last_action = 'Turn ON at: %s' % self.rtc.isoformat()

    def _turn_off(self):
        self.pins.relay.off()
        self.last_action = 'Turn OFF at: %s' % self.rtc.isoformat()

    def _timer_callback(self, timer):
        gc.collect()
        self.check_count += 1
        self.last_check = self.rtc.isoformat()
        if not self.active:
            self.last_action = 'timer not active'
            return
        gc.collect()

        if self.on_time is None and self.off_time is None:
            self.last_action = 'no timer set'
            return

        if self.off_time is None and self.rtc.later(self.on_time):
            self._turn_on()
        elif self.on_time is None and self.rtc.later(self.off_time):
            self._turn_off()
        elif self.rtc.in_time_range(self.on_time, self.off_time):
            self._turn_on()
        else:
            self._turn_off()

    def deinit(self):
        self.timer.deinit()

    def __str__(self):
        return (
            'AutomaticTimer -'
            ' last check: %s,'
            ' check count: %s,'
            ' last action: %s'
        ) % (
            self.last_check, self.check_count, self.last_action
        )
