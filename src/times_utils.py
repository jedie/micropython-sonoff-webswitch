
# import sys

import ure
import utime
from micropython import const

_TIMERS_PY_CFG_NAME = 'timers'
_ACTIVE_DAYS_PY_CFG_NAME = 'timer_days'
_SEC2MS = const(60 * 1000)
_ONE_DAY_SEC = const(1 * 24 * 60 * 60)


def parse_time(clock_time):
    hours, minutes = clock_time.split(':')
    return int(hours), int(minutes)


def iter_times(times):
    """
    yield turn_on, hour:min:sec from every timer
    """
    for start, stop in times:
        assert isinstance(start, tuple)
        assert isinstance(stop, tuple)
        # Adds 00 seconds to start/stop,
        # that makes processing later much easier
        yield True, start + (0,)
        yield False, stop + (0,)


def validate_times(times):
    old_time = 0
    for turn_on, (hours, minutes, seconds) in iter_times(times):
        assert seconds == 0
        if not (0 <= hours <= 23 and 0 <= minutes <= 59):
            raise ValueError('%02i:%02i is not valid' % (hours, minutes))
        new_time = minutes + (hours * 60)
        if new_time <= old_time:
            raise ValueError('%02i:%02i is in wrong order' % (hours, minutes))
        old_time = new_time
    return True


def parse_timers(data):
    regex = ure.compile(r'^\D*(\d+:\d+)\D+(\d+:\d+)\D*$')
    data = data.strip()

    last_time = None
    for no, line in enumerate(data.split('\n'), 1):
        line = line.strip()
        if not line:
            continue

        match = regex.match(line)
        if not match:
            print('Error in: %r' % line)
            raise ValueError('Wrong time in line %i' % no)

        start_time = parse_time(match.group(1))
        end_time = parse_time(match.group(2))

        if start_time >= end_time or (last_time is not None and start_time <= last_time):
            print('Error in: %r' % line)
            raise ValueError('Times in line %i are not sequential!' % no)

        last_time = end_time
        yield (start_time, end_time)


def pformat_timers(times):
    return '\n'.join(
        [
            '%02i:%02i - %02i:%02i' % (t[0][0], t[0][1], t[1][0], t[1][1])
            for t in times
        ]
    )


def save_timers(times):
    from config_files import save_py_config
    save_py_config(module_name=_TIMERS_PY_CFG_NAME, value=times)

    # del save_py_config
    # del sys.modules['config_files']


def restore_timers():
    from config_files import restore_py_config
    timers = restore_py_config(module_name=_TIMERS_PY_CFG_NAME, default=())

    # del restore_py_config
    # del sys.modules['config_files']

    return timers


def get_active_days():
    from config_files import restore_py_config
    active_days = restore_py_config(module_name=_ACTIVE_DAYS_PY_CFG_NAME, default=tuple(range(7)))

    # del restore_py_config
    # del sys.modules['config_files']

    return active_days


def save_active_days(active_days):
    from config_files import save_py_config
    save_py_config(module_name=_ACTIVE_DAYS_PY_CFG_NAME, value=active_days)

    # del save_py_config
    # del sys.modules['config_files']


def human_timer_duration(epoch):
    sec = epoch - utime.time()
    if abs(sec) > (2 * 60 * 60):
        return '%i h' % (sec / 60 / 60)
    if abs(sec) >= 60:
        return '%i min' % (sec / 60)
    return '%i sec' % sec


class Timers:
    def __init__(self):
        (
            self.year, self.month, self.mday,
            self.hour, self.minute, self.second,
            self.weekday, self.yearday
        ) = utime.localtime(
            utime.time() + 1  # use the time 1sec in the future as reference ;)
        )

    def get_current_timer(self):
        """
        return last and next switching point in "(hours, minutes)"
        and if the next point turns ON or OFF
        """
        turn_on_times = tuple(iter_times(restore_timers()))

        now_hour_minute_sec = (self.hour, self.minute, self.second)
        # print('%02i:%02i:%02i' % now_hour_minute_sec)

        no = None
        next_timer = None
        for no, (turn_on, hour_minute_sec) in enumerate(turn_on_times):
            # print('Timer:', no, turn_on, hour_minute_sec)
            if hour_minute_sec >= now_hour_minute_sec:
                next_timer = hour_minute_sec
                break

        if no is None:
            # print('No timers scheduled')
            return (None, None, None)

        if next_timer is None:
            print('Next timer is on next day:', turn_on_times[0][1])
            return (
                self.hour_minute_sec2epoch(turn_on_times[-1][1]),  # Previous timer is the last
                True,  # Turn ON next day
                self.hour_minute_sec2epoch(turn_on_times[0][1]) + _ONE_DAY_SEC,  # Shift to next day
            )
        else:
            print('Next timer found:', next_timer)
            previous_timer = self.hour_minute_sec2epoch(turn_on_times[no - 1][1])
            if no == 0:
                # previous timer was on last day -> shift one day back
                previous_timer -= _ONE_DAY_SEC

            return (
                previous_timer,
                turn_on,
                self.hour_minute_sec2epoch(next_timer)
            )

    def hour_minute_sec2epoch(self, hour_minute_sec):
        hour, minute, second = hour_minute_sec
        return utime.mktime(
            (
                self.year, self.month, self.mday,
                hour, minute, second,
                self.weekday, self.yearday
            )
        )


def get_next_timer():
    return Timers().get_current_timer()
