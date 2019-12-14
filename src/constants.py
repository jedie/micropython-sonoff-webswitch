from micropython import const

RTC_KEY_RESET_REASON = 'reset-reason'
RTC_KEY_WATCHDOG_COUNT = 'watchdog-reset'

WEBSERVER_HOST = '0.0.0.0'
WEBSERVER_PORT = const(80)

WATCHDOG_CHECK_PERIOD = const(50 * 1000)  # 50 sec
WATCHDOG_TIMEOUT = const(30)

WIFI_TIMEOUT = const(20 * 1000)  # 20 sec

POWER_TIMER_ACTIVE_KEY = 'active'
POWER_TIMER_WEEKDAYS_KEY = 'days'

CHUNK_SIZE = const(512)

# constants will not be cleared from sys.modules
# So this buffer should be not freed by garbage collection
BUFFER = memoryview(bytearray(CHUNK_SIZE))
