

import gc
import sys

import constants
import machine
import micropython
import utime


class Watchdog:
    timer = machine.Timer(-1)

    def __init__(self, context):
        self.context = context

        print('Start Watchdog period timer')
        self.timer.deinit()
        self.timer.init(
            period=constants.WATCHDOG_CHECK_PERIOD,
            mode=machine.Timer.PERIODIC,
            callback=self._timer_callback
        )

    def _timer_callback(self, timer):
        from watchdog_checks import check
        check(context=self.context)
        # del check

        self.context.watchdog_check_count += 1

        from timezone import localtime_isoformat
        self.context.watchdog_last_check = localtime_isoformat()

        self.garbage_collection()

    def feed(self):
        self.context.watchdog_last_feed = utime.time()

    def garbage_collection(self):
        print('\n')
        micropython.mem_info()

        if self.context.minimal_modules is None:
            print('context.minimal_modules not set, yet!')
        else:
            for module_name in [
                    name for name in sys.modules.keys()
                    if name not in self.context.minimal_modules
            ]:
                print('remove obsolete module: %r' % module_name)
                del sys.modules[module_name]

        gc.collect()
        # gc.threshold(gc.mem_free() // 4 + gc.mem_alloc())

        micropython.mem_info()
