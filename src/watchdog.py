

import gc
import sys

import constants
import machine
import utime


class Watchdog:
    timer = machine.Timer(-1)

    def __init__(self, context):
        self.context = context

        self.timer.deinit()
        self.timer.init(
            period=constants.WATCHDOG_CHECK_PERIOD,
            mode=machine.Timer.PERIODIC,
            callback=self._timer_callback
        )

    def _timer_callback(self, timer):
        from watchdog_checks import check
        check(context=self.context)

        self.context.watchdog_check_count += 1
        self.context.watchdog_last_check = utime.time()

        self.garbage_collection()

    def feed(self):
        self.context.watchdog_last_feed = utime.time()

    def garbage_collection(self):
        print('\n')
        # micropython.mem_info(1)
        previous = gc.mem_free()

        if self.context.minimal_modules is not None:
            for module_name in [
                    name for name in sys.modules.keys()
                    if name not in self.context.minimal_modules
            ]:
                print('remove:', module_name)
                del sys.modules[module_name]

        gc.collect()
        free = gc.mem_free()
        print('freed up %i bytes -> %i bytes free' % (free - previous, free))

        # micropython.mem_info(1)
