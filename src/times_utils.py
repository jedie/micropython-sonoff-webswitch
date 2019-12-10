

_TIMERS_FILENAME = 'timers.txt'
_ACTIVE_DAYS_FILENAME = 'timer_days.txt'


def parse_time(clock_time):
    hours, minutes = clock_time.split(':')
    return int(hours), int(minutes)


def iter_times(times):
    for start, stop in times:
        yield start
        yield stop


def validate_times(times):
    old_time = 0
    for hours, minutes in iter_times(times):
        print(hours, minutes)
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
    if tuple(restore_timers()) == times:
        # Don't save if the same timers already exists
        return

    with open(_TIMERS_FILENAME, 'w') as f:
        for t in times:
            f.write('%i:%i-%i:%i\n' % (t[0][0], t[0][1], t[1][0], t[1][1]))


def restore_timers():
    try:
        with open(_TIMERS_FILENAME, 'r') as f:
            yield from parse_timers(f.read())
    except OSError:
        print('File not exists: %r' % _TIMERS_FILENAME)


def get_active_days():
    try:
        with open(_ACTIVE_DAYS_FILENAME, 'r') as f:
            return tuple([int(d) for d in f.read().split(',')])
    except OSError:
        print('File not exists: %r' % _ACTIVE_DAYS_FILENAME)
        return tuple(range(7))


def save_active_days(active_days):
    if tuple(get_active_days()) == active_days:
        # Don't save if same active days already exists
        return

    with open(_ACTIVE_DAYS_FILENAME, 'w') as f:
        f.write(','.join([str(d) for d in active_days]))


def get_next_timer(current_time):
    """
    return next next switching point

    :param current_time: machine.RTC().datetime()[4:6]
    :return: (bool, (hour, minute))
    """
    first_time = None
    for no, time in enumerate(iter_times(restore_timers())):
        if no == 0:
            first_time = time

        if time > current_time:
            return (not bool(no % 2)), time

    if first_time:
        # After the last switching point,
        # the next day is switched on again
        # at the first switching point.
        return True, first_time

    return None, None


def get_ms_until_next_timer(current_time):
    """
    return time in ms until the next switching point.

    :param current_time: machine.RTC().datetime()[4:6]
    :return: (bool, ms)
    """
    turn_on, next_time = get_next_timer(current_time)
    if turn_on is None:
        return None, None, None

    current_time_sec = (current_time[0] * 60) + current_time[1]
    next_time_sec = (next_time[0] * 60) + next_time[1]

    return turn_on, next_time, (next_time_sec - current_time_sec) * 1000
