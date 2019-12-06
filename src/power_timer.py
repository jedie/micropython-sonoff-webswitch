import gc
import sys

import machine
from pins import Pins


class PowerTimer:
    last_update = None
    next_time = None
    next_time_ms = None
    turn_on = None  # turn power switch next time on or off ?
    active = None  # are timers activated ?
    timer = machine.Timer(-1)

    def schedule_next_switch(self):
        from power_timer_schedule import update_power_timer

        update_power_timer(power_timer=self)

        del update_power_timer
        del sys.modules['power_timer_schedule']
        gc.collect()

    def _timer_callback(self, timer):
        assert self.active is True
        if self.turn_on:
            Pins.relay.on()
        else:
            Pins.relay.off()

    def reset(self):
        self.timer.deinit()
        self.next_time = None
        self.next_time_ms = None
        self.turn_on = None
        self.active = False

    def __str__(self):
        if not self.active:
            return 'Power timer is not active.'

        if self.next_time < 0:
            self.reset()
            return 'missed timer'

        if self.turn_on is None:
            return 'No switch scheduled. (Last update: %s)' % self.last_update
        else:
            return 'Switch %s in %i sec. at %02i:%02i h. (Last update: %s)' % (
                'on' if self.turn_on else 'off',
                (self.next_time_ms / 1000),
                self.next_time[0], self.next_time[1],
                self.last_update
            )
