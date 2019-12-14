import gc
import sys

import machine
import utime
from pins import Pins


class PowerTimer:
    last_update = None
    next_timer_epoch = None
    turn_on = None  # turn power switch next time on or off ?
    active = None  # are timers activated ?
    today_active = None  # Is the timer active this weekday ?
    timer = machine.Timer(-1)

    def schedule_next_switch(self):
        from power_timer_schedule import update_power_timer

        update_power_timer(power_timer=self)

        del update_power_timer
        del sys.modules['power_timer_schedule']
        gc.collect()

    def _timer_callback(self, timer):
        print('Power timer called!')
        assert self.active is True
        if self.turn_on:
            print('switch on')
            Pins.relay.on()
        else:
            print('switch off')
            Pins.relay.off()

    def timer_hour_min(self):
        timer_tuple = utime.localtime(self.next_timer_epoch)
        # year, month, mday, hour, minute, second, weekday, yearday
        return timer_tuple[3], timer_tuple[4]

    @property
    def timer_in_sec(self):
        if self.next_timer_epoch is not None:
            return self.next_timer_epoch - utime.time()
        return -1

    @property
    def missed_timer(self):
        if self.next_timer_epoch is not None:
            return self.timer_in_sec <= 0

    def human_timer_duration(self):
        sec = self.timer_in_sec
        if sec > (2 * 60 * 60):
            return '%i h' % (sec / 60 / 60)
        if sec >= 60:
            return '%i min' % (sec / 60)
        return '%i sec' % sec

    def info_text(self):
        if not self.active:
            return 'Power timer is deactivated. (Last update: %s)' % self.last_update

        if self.missed_timer:
            self.next_timer_epoch = None
            return 'missed timer (Last update: %s)' % self.last_update

        if self.today_active is False:
            return 'Power timer is not active today. (Last update: %s)' % self.last_update

        if self.next_timer_epoch is None:
            return 'No switch scheduled. (Last update: %s)' % self.last_update

        timer_hour, timer_min = self.timer_hour_min()
        return 'Switch %s in %s at %02i:%02i h. (Last update: %s)' % (
            'on' if self.turn_on else 'off',
            self.human_timer_duration(),
            timer_hour, timer_min,
            self.last_update
        )

    def __str__(self):
        return (
            'last_update=%r,'
            ' next_timer_epoch=%r,'
            ' turn_on=%r,'
            ' active=%r,'
            ' today_active=%r'
        ) % (
            self.last_update,
            self.next_timer_epoch,
            self.turn_on,
            self.active,
            self.today_active,
        )
