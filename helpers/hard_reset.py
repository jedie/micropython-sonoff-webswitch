if __name__ == '__main__':
    print(' *** Hard reset ! ***')

    import machine
    machine.reset()

    import utime
    utime.sleep(1)

    print('sys.exit()')
    import sys
    sys.exit()
