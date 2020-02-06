

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
        gc.collect()

        from watchdog_checks import check
        check(context=self.context)

        self.context.watchdog_check_count += 1

        self.garbage_collection()

    def feed(self):
        """
        Will be called from webswitch.WebServer.periodical_tasks()
        """
        self.context.watchdog_last_feed_epoch = utime.time()

    def collect_import_cache(self):
        if self.context.minimal_modules is not None:
            return

        for module_name in [
                name for name in sys.modules.keys()
                if name not in self.context.minimal_modules
        ]:
            print('remove:', module_name)
            del sys.modules[module_name]

    def garbage_collection(self):
        print('\nWatchdog.garbage_collection():')
        previous = gc.mem_free()
        self.collect_import_cache()
        gc.collect()
        free = gc.mem_free()
        print('freed up %i bytes -> %i bytes free' % (free - previous, free))
