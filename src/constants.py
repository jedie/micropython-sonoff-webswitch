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

TIMERS_PY_CFG_NAME = 'timers'
ACTIVE_DAYS_PY_CFG_NAME = 'timer_days'

MIME_TYPES = {
    'ico': b'image/x-icon',
    'css': b'text/css',
}
CONTENT_TYPE = b'Content-Type: %s\r\n'
HTTP_LINE_200 = b'HTTP/1.0 200 OK\r\n'
HTTP_LINE_303 = b'HTTP/1.0 303 Moved\r\n'
HTTP_LINE_LOCATION = 'Location: {url}\r\n\r\n'
HTTP_LINE_CACHE = b'Cache-Control: max-age=6000\r\n'

CHUNK_SIZE = const(512)

# constants will not be cleared from sys.modules
# So this buffer should be not freed by garbage collection
BUFFER = memoryview(bytearray(CHUNK_SIZE))

# Save power state change via button or web page:
RTC_KEY_MANUAL_OVERWRITE = 'manual'
RTC_KEY_MANUAL_OVERWRITE_TYPE = 'manual-type'

H2SEC = const(60 * 60)  # multiplier for calc hours into seconds
ONE_DAY_SEC = const(1 * 24 * 60 * 60)
NTP_MIN_TIME_EPOCH = const(599616000)  # epoch 1.1.2019
NTP_SYNC_WAIT_TIME_SEC = const(1 * 60 * 60)  # sync NTP every 1 h

TIMEZONE_PY_CFG_NAME = 'timezone'
DEFAULT_OFFSET_H = const(0)

JSON_CFG_FILE_PATTERN = '_config_%s.json'  # e.g.: _config_foobar.json
PY_MODULE_NAME_PATTERN = '_config_%s'  # e.g.: _config_foobar
PY_FILE_PATTERN = '_config_%s.py'  # e.g.: _config_foobar.py
