import gc
import sys

import network
import utime as time


class WiFi:
    connected_time = 0
    last_ntp_sync = 0

    not_connected_count = 0
    is_connected_count = 0
    last_refresh = None
    verbose = True

    def __init__(self, rtc, power_led):
        self.rtc = rtc
        self.power_led = power_led
        self.power_led.off()

        print('Setup WiFi interfaces')
        self.access_point = network.WLAN(network.AP_IF)  # access-point interface
        self.station = network.WLAN(network.STA_IF)  # WiFi station interface
        self.station.active(True)  # activate the interface

    @property
    def is_connected(self):
        if not self.station.isconnected():
            if self.verbose:
                print('Not connected to station!')
            self.power_led.off()
            return False
        else:
            self.connected_time = time.time()
            if self.verbose:
                print('Connected to station IP/netmask/gw/DNS addresses:', self.station.ifconfig())
            self.power_led.on()

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

            if time.time() > self.last_ntp_sync:
                from ntp import ntp_sync
                ntp_sync(rtc=self.rtc)  # update RTC via NTP
                del ntp_sync
                del sys.modules['ntp']
                self.last_ntp_sync = time.time()

            self.last_refresh = self.rtc.isoformat()
            return

        self.not_connected_count += 1

        self.power_led.flash(sleep=0.1, count=5)

        if self.verbose:
            print('read WiFi config...')

        from get_config import get_config
        wifi_configs = get_config(key='wifi')

        known_ssid = self.get_known_ssid(wifi_configs)
        if known_ssid is None:
            print('Skip Wifi connection.')
        else:
            self._connect(known_ssid, password=get_config(key='wifi')[known_ssid])

        gc.collect()

    def get_known_ssid(self, wifi_configs):
        print('Scan WiFi...')

        known_ssid = None
        for no in range(3):
            for info in self.station.scan():
                self.power_led.toggle()
                ssid, bssid, channel, RSSI, auth_mode, hidden = info
                ssid = ssid.decode("UTF-8")
                if self.verbose:
                    print(
                        'SSID: %s (channel: %s authmode: %s hidden: %s)' % (
                            ssid, channel, auth_mode, hidden
                        )
                    )
                if ssid in wifi_configs:
                    known_ssid = ssid
            if known_ssid is not None:
                return known_ssid

        print('ERROR: No known WiFi SSID found!')
        self.power_led.flash(sleep=0.2, count=20)

    def _connect(self, ssid, password):
        for no in range(0, 3):
            if self.verbose:
                print('PHY mode: %s' % network.phy_mode())
            # print('Connect to Wifi access point:', ssid, repr(password))
            if self.verbose:
                print('Connect to Wifi access point: %s' % ssid)
            self.power_led.toggle()
            self.station.connect(ssid, password)
            for wait_sec in range(30, 1, -1):
                status = self.station.status()
                if status == network.STAT_GOT_IP:
                    self.connected_time = time.time()
                    self.power_led.on()
                    return
                elif status == network.STAT_WRONG_PASSWORD:
                    print('Wrong password!')
                    return
                if self.verbose:
                    print('wait %i...' % wait_sec)
                self.power_led.flash(sleep=0.1, count=10)

            if self.verbose:
                print('Try again...')
            self.station.active(False)
            self.power_led.flash(sleep=0.1, count=20)
            self.power_led.off()
            self.station.active(True)

        print("ERROR: WiFi not connected! Password wrong?!?")
        self.power_led.flash(sleep=0.2, count=20)

    def __str__(self):
        return 'WiFi last refresh: %s - connected: %i - not connected: %i' % (
            self.last_refresh, self.is_connected_count, self.not_connected_count
        )
