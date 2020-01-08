import gc
import sys

import constants
import ure
import utime
from micropython import const

MAX_DAY_MINUTES = const(24 * 60 + 59)


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
    gc.collect()
    return True


def clock_time2minutes(clock_time):
    hours, minutes = clock_time.split(':')
    return int(hours) * 60 + int(minutes)


def minutes2clock_time(minutes):
    hours = int(minutes / 60)
    minutes = minutes - (hours * 60)
    return hours, minutes


def timers2list(data):
    print('parse_timers:', repr(data))
    regex = ure.compile(r'^\D*(\d+:\d+)\D+(\d+:\d+)\D*$')
    data = data.strip().replace('\r\n', '\n').split('\n')

    times = []
    for line_no, line in enumerate(data, 1):
        print(line_no, repr(line))
        line = line.strip()
        if not line:
            continue

        match = regex.match(line)
        if not match:
            print('Error in: %r' % line)
            raise ValueError('Wrong time in line %i' % line_no)

        start_minutes = clock_time2minutes(match.group(1))
        end_minutes = clock_time2minutes(match.group(2))

        del match  # collect match object
        gc.collect()

        if not 0 <= start_minutes <= MAX_DAY_MINUTES:
            print('Error in start time: %r' % line)
            raise ValueError('No valid start time in %i!' % line_no)

        if not 0 <= end_minutes <= MAX_DAY_MINUTES:
            print('Error in end time: %r' % line)
            raise ValueError('No valid end time in %i!' % line_no)

        if start_minutes >= end_minutes:
            print('Error in: %r (%r >= %r)' % (line, start_minutes, end_minutes))
            raise ValueError('Times in line %i are not sequential!' % line_no)

        times.append(start_minutes)
        times.append(end_minutes)

    times.sort()
    return times


def parse_timers(data):
    times = timers2list(data)
    gc.collect()

    last_time = None
    pos = 0
    line_no = 1
    while pos < len(times):
        start_minutes = times[pos]
        pos += 1
        end_minutes = times[pos]

        print(
            line_no,
            start_minutes,
            end_minutes,
            minutes2clock_time(start_minutes),
            minutes2clock_time(end_minutes))

        if last_time is not None and start_minutes <= last_time:
            raise ValueError('Times in line %i are not sequential!' % line_no)

        yield (minutes2clock_time(start_minutes), minutes2clock_time(end_minutes))

        last_time = end_minutes
        pos += 1
        line_no += 1


def pformat_timers(times):
    return '\n'.join(
        [
            '%02i:%02i - %02i:%02i' % (t[0][0], t[0][1], t[1][0], t[1][1])
            for t in times
        ]
    )


def restore_timers():
    from config_files import restore_py_config
    timers = restore_py_config(
        module_name=constants.TIMERS_PY_CFG_NAME,
        default=()
    )

    del restore_py_config
    del sys.modules['config_files']
    gc.collect()

    return timers


def get_active_days():
    from config_files import restore_py_config
    active_days = restore_py_config(
        module_name=constants.ACTIVE_DAYS_PY_CFG_NAME,
        default=tuple(range(7))
    )

    del restore_py_config
    del sys.modules['config_files']
    gc.collect()

    return active_days


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

    def get_current_timer(self, context):
        """
        return last and next switching point in "(hours, minutes)"
        and if the next point turns ON or OFF
        """
        assert context.power_timer_timers is not None, 'Timers not loaded, yet?!?'
        turn_on_times = tuple(iter_times(context.power_timer_timers))

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
                # Previous timer is the last:
                self.hour_minute_sec2epoch(turn_on_times[-1][1]),
                # Turn ON next day:
                True,
                # Shift to next day:
                self.hour_minute_sec2epoch(turn_on_times[0][1]) + constants.ONE_DAY_SEC,
            )
        else:
            print('Next timer found:', next_timer)
            previous_timer = self.hour_minute_sec2epoch(turn_on_times[no - 1][1])
            if no == 0:
                # previous timer was on last day -> shift one day back
                previous_timer -= constants.ONE_DAY_SEC

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


def get_current_timer(context):
    current_timer = Timers().get_current_timer(context)
    gc.collect()
    return current_timer
