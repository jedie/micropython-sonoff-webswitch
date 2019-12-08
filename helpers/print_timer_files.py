_TIMERS_FILENAME = 'timers.txt'
_ACTIVE_DAYS_FILENAME = 'timer_days.txt'


def print_files(file_name):
    print('_' * 79)
    print(file_name)
    with open(file_name, 'r') as f:
        print(f.read())
    print('-' * 79)


print_files(_TIMERS_FILENAME)
print_files(_ACTIVE_DAYS_FILENAME)
