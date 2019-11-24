
import utime as time
from watchdog import Watchdog, watchdog


def test(watchdog):
    print('test start...')
    watchdog.deinit()  # deinit global watchdog

    # Create new one with shorter timeout:
    watchdog = Watchdog(
        check_period=3 * 1000,  # 2 sec
        timeout=2 * 1000,  # 1 sec
    )
    print(watchdog)
    for _ in range(10):
        print('.', end='')
        time.sleep(0.5)
        watchdog.feed()
    print('\nfeed end\n')

    print(watchdog)

    while True:
        print(watchdog)
        time.sleep(0.5)


if __name__ == '__main__':
    test(watchdog)  # will reset the device !
    print('test end.')  # should never happen
