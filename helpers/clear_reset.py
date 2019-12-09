"""
    Delete 'main.py' and hard reset, for experiments via REPL
"""

import sys

sys.modules.clear()


def main():
    import gc
    gc.collect()

    print('DELETE: main.py !!!')
    import uos
    try:
        uos.remove('main.py')
    except BaseException:
        # already deleted?
        pass

    print('Hard reset !')

    import machine
    machine.reset()

    import utime
    utime.sleep(1)

    print('sys.exit()')
    import sys
    sys.exit()


if __name__ == '__main__':
    main()
