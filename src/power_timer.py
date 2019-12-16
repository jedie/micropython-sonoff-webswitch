import gc
import sys

import utime


class PowerTimer:
    last_update = None
    next_timer_epoch = None
    turn_on = None  # turn power switch next time on or off ?
    active = None  # are timers activated ?
    today_active = None  # Is the timer active this weekday ?

    def update_relay_switch(self):
        from power_timer_schedule import update_power_timer

        update_power_timer(power_timer=self)

        del update_power_timer
        del sys.modules['power_timer_schedule']
        gc.collect()

    def info_text(self):
        if not self.active:
            return 'Power timer is deactivated. (Last update: %s)' % self.last_update

        if self.today_active is False:
            return 'Power timer is not active today. (Last update: %s)' % self.last_update

        if self.next_timer_epoch is None:
            return 'No switch scheduled. (Last update: %s)' % self.last_update

        # year, month, mday, hour, minute, second, weekday, yearday
        timer_hour, timer_min = utime.localtime(self.next_timer_epoch)[3:5]
        from times_utils import human_timer_duration
        return 'Switch %s in %s at %02i:%02i h. (Last update: %s)' % (
            'on' if self.turn_on else 'off',
            human_timer_duration(self.next_timer_epoch),
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
