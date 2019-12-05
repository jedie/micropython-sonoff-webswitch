
try:
    import ure as re
except ImportError:
    import re

_TIMERS_FILENAME = 'timers.txt'


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
    if restore_timers() == times:
        # Don't save if the same timers already exists
        return

    with open(_TIMERS_FILENAME, 'w') as f:
        for t in times:
            f.write('%i:%i-%i:%i\n' % (t[0][0], t[0][1], t[1][0], t[1][1]))


def restore_timers():
    try:
        with open(_TIMERS_FILENAME, 'r') as f:
            return tuple(parse_timers(f.read()))
    except OSError:
        print('File not exists: %r' % _TIMERS_FILENAME)
        return ()