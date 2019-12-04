import gc

from pins import Pins
from rtc import get_rtc_value, rtc_in_time_range, rtc_isoformat, rtc_later, update_rtc_dict


def parse_get_time(raw):
    if raw:
        hours, minutes = raw.split('%3A')
        hours = int(hours)
        minutes = int(minutes)
        return hours, minutes


def set_timer_from_web(get_parameters):
    update_rtc_dict(data={
        'on': parse_get_time(get_parameters['on']),
        'off': parse_get_time(get_parameters['off']),
        'active': get_parameters['active'] == 'on'
    })


def get_timer_form_value(key):
    value = get_rtc_value(key)
    if not value:
        return ''
    return '%02i:%02i' % (value[0], value[1])


class AutomaticTimer:
    last_check = 0
    check_count = 0
    last_action = None

    @property
    def on_time(self):
        return get_rtc_value('on')

    @property
    def off_time(self):
        return get_rtc_value('off')

    @property
    def active(self):
        return get_rtc_value('active', False)

    def _turn_on(self):
        Pins.relay.on()
        self.last_action = 'Turn ON at: %s' % rtc_isoformat()

    def _turn_off(self):
        Pins.relay.off()
        self.last_action = 'Turn OFF at: %s' % rtc_isoformat()

    def timer_callback(self):
        gc.collect()
        self.check_count += 1
        self.last_check = rtc_isoformat()
        if not self.active:
            self.last_action = 'timer not active'
            return
        gc.collect()

        if self.on_time is None and self.off_time is None:
            self.last_action = 'no timer set'
            return

        if self.off_time is None and rtc_later(self.on_time):
            self._turn_on()
        elif self.on_time is None and rtc_later(self.off_time):
            self._turn_off()
        elif rtc_in_time_range(self.on_time, self.off_time):
            self._turn_on()
        else:
            self._turn_off()

    def __str__(self):
        return (
            'AutomaticTimer -'
            ' last check: %s,'
            ' check count: %s,'
            ' last action: %s'
        ) % (
            self.last_check, self.check_count, self.last_action
        )
