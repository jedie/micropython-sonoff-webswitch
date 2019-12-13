import gc
import sys

import network
import utime
from micropython import const
from pins import Pins

_NTP_SYNC_WAIT_TIME_SEC = const(1 * 60 * 60)  # sync NTP every 1 h
_MIN_TIME_EPOCH = const(599616000)  # epoch 1.1.2019


class WiFi:
    connected_time = 0
    next_ntp_sync = 0
    last_ntp_sync = None

    not_connected_count = 0
    is_connected_count = 0
    last_refresh = None
    verbose = True

    def __init__(self):
        Pins.power_led.off()

        print('Setup WiFi interfaces')
        self.access_point = network.WLAN(network.AP_IF)  # access-point interface
        self.station = network.WLAN(network.STA_IF)  # WiFi station interface
        self.station.active(True)  # activate the interface

    @property
    def is_connected(self):
        if not self.station.isconnected():
            if self.verbose:
                print('Not connected to station!')
            Pins.power_led.off()
            return False
        else:
            self.connected_time = utime.time()
            if self.verbose:
                print('Connected to station IP/netmask/gw/DNS addresses:', self.station.ifconfig())
            Pins.power_led.on()

            if self.access_point.active():
                if self.verbose:
                    print('deactivate access-point interface...')
                self.access_point.active(False)

            self.verbose = False
            return True

    def ensure_connection(self):
        if self.verbose:
            print('WiFi ensure connection...', end=' ')

        gc.collect()
        if self.is_connected:
            self.is_connected_count += 1

            from timezone import localtime_isoformat

            if self.next_ntp_sync < utime.time():
                from ntp import ntp_sync
                sync_done = ntp_sync()  # update RTC via NTP
                del ntp_sync
                del sys.modules['ntp']
                if sync_done and utime.time() > _MIN_TIME_EPOCH:
                    self.next_ntp_sync = utime.time() + _NTP_SYNC_WAIT_TIME_SEC
                    self.last_ntp_sync = localtime_isoformat()

            self.last_refresh = localtime_isoformat()

            del localtime_isoformat
            del sys.modules['timezone']
            gc.collect()
            return

        self.not_connected_count += 1

        from wifi_connect import connect
        self.connected_time = connect(station=self.station, verbose=self.verbose)

        del connect
        del sys.modules['wifi_connect']
        gc.collect()

    def __str__(self):
        return (
            'last refresh: %s'
            ' - connected: %i'
            ' - not connected: %i'
            ' - last NTP sync: %s'
        ) % (
            self.last_refresh, self.is_connected_count, self.not_connected_count,
            self.last_ntp_sync
        )
