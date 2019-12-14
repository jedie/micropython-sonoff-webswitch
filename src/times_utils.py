import gc
import sys

from micropython import const

_TIMERS_PY_CFG_NAME = 'timers'
_ACTIVE_DAYS_PY_CFG_NAME = 'timer_days'
_SEC2MS = const(60 * 1000)


def parse_time(clock_time):
    hours, minutes = clock_time.split(':')
    return int(hours), int(minutes)


def iter_times(times):
    for start, stop in times:
        assert isinstance(start, tuple)
        assert isinstance(stop, tuple)
        yield True, start
        yield False, stop


def validate_times(times):
    old_time = 0
    for turn_on, (hours, minutes) in iter_times(times):
        if not (0 <= hours <= 23 and 0 <= minutes <= 59):
            raise ValueError('%02i:%02i is not valid' % (hours, minutes))
        new_time = minutes + (hours * 60)
        if new_time <= old_time:
            raise ValueError('%02i:%02i is in wrong order' % (hours, minutes))
        old_time = new_time
    return True


def parse_timers(data):
    import ure as re
    regex = re.compile(r'^\D*(\d+:\d+)\D+(\d+:\d+)\D*$')
    data = data.strip()

    for no, line in enumerate(data.split('\n'), 1):
        line = line.strip()
        if not line:
            continue

        match = regex.match(line)
        if not match:
            print('Error in: %r' % line)
            raise ValueError('Wrong time in line %i' % no)

        yield (parse_time(match.group(1)), parse_time(match.group(2)))


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

    del save_py_config
    del sys.modules['config_files']
    gc.collect()


def restore_timers():
    from config_files import restore_py_config
    timers = restore_py_config(module_name=_TIMERS_PY_CFG_NAME, default=())

    del restore_py_config
    del sys.modules['config_files']
    gc.collect()
    return timers


def get_active_days():
    from config_files import restore_py_config
    active_days = restore_py_config(module_name=_ACTIVE_DAYS_PY_CFG_NAME, default=tuple(range(7)))

    del restore_py_config
    del sys.modules['config_files']
    gc.collect()
    return active_days


def save_active_days(active_days):
    from config_files import save_py_config
    save_py_config(module_name=_ACTIVE_DAYS_PY_CFG_NAME, value=active_days)

    del save_py_config
    del sys.modules['config_files']
    gc.collect()


def get_next_timer():
    """
    return next next switching point

    :param current_time: get_localtime()[4:6]
    :return: (bool, (hour, minute))
    """
    import utime

    local_time_tuple = utime.localtime()
    local_epoch = utime.mktime(local_time_tuple)

    local_time_prefix = local_time_tuple[:3]  # year, month, mday
    local_time_suffix = local_time_tuple[5:]  # second, weekday, yearday

    for turn_on, hours_minutes in iter_times(restore_timers()):
        # print('Timer:', hours_minutes)
        timer_epoch = utime.mktime(local_time_prefix + hours_minutes + local_time_suffix)

        if timer_epoch > local_epoch:
            # print('Next timer:', utime.localtime(timer_epoch))
            return turn_on, timer_epoch

    return None, None


if __name__ == '__main__':
    print('test...')
    from timezone import localtime_isoformat

    timers = tuple(parse_timers('''
         6:00 -  7:00
        19:00 - 20:00
    '''))
    print('Overwrite timers with:', timers)
    save_timers(timers)

    print(localtime_isoformat(sep=' '))
    turn_on, timer_epoch = get_next_timer()
    print('get_ms_until_next_timer():', turn_on, timer_epoch)
    print(localtime_isoformat(sep=' ', epoch=timer_epoch))
