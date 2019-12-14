import sys

sys.modules.clear()


def main():
    import gc
    gc.collect()

    import utime
    from reset import ResetDevice

    ResetDevice(reason='Test reset in 5 sec.').schedule(period=5000)
    start_time = utime.time()
    for i in range(7):
        print('Time passed: %isec...' % (utime.time() - start_time))
        utime.sleep(1)

    print('Error!')


if __name__ == '__main__':
    main()
