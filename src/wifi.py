import gc
import sys

import constants
import machine
import network
import ntptime
import utime as time
from leds import power_led
from watchdog import watchdog

gc.collect()
rtc = machine.RTC()


class WiFi:
    not_connected_count = 0
    is_connected_count = 0
    last_refresh = None

    timer = machine.Timer(-1)

    def __init__(self):
        print('Setup WiFi interfaces')
        self.access_point = network.WLAN(network.AP_IF)  # access-point interface
        self.station = network.WLAN(network.STA_IF)  # WiFi station interface
        self.station.active(True)  # activate the interface

        print('ensure connection on init')
        self._ensure_connection()

        print('Start WiFi period timer')
        self.timer.deinit()
        self.timer.init(
            period=constants.WIFI_TIMER,
            mode=machine.Timer.PERIODIC,
            callback=self._timer_callback)

    @property
    def is_connected(self):
        if not self.station.isconnected():
            print('Not connected to station!')
            power_led.off()
            return False
        else:
            print('Connected to station IP/netmask/gw/DNS addresses:', self.station.ifconfig())
            power_led.on()
            watchdog.feed()

            if self.access_point.active():
                print('deactivate access-point interface...')
                self.access_point.active(False)

            return True

    def _timer_callback(self, timer):
        print('WiFi timer callback for:', timer)
        try:
            self._ensure_connection()
        except Exception as e:
            sys.print_exception(e)
            self.timer.deinit()

    def _ensure_connection(self):
        print('WiFi ensure connection...', end=' ')
        gc.collect()
        if self.is_connected:
            self.is_connected_count += 1
            self.last_refresh = rtc.datetime()
            return

        self.not_connected_count += 1

        power_led.flash(sleep=0.1, count=5)

        print('read WiFi config...')
        from get_config import config
        wifi_configs = config['wifi']

        known_ssid = self.get_known_ssid(wifi_configs)
        if known_ssid is None:
            print('Skip Wifi connection.')
        else:
            self._connect(known_ssid, password=config['wifi'][known_ssid])

    def get_known_ssid(self, wifi_configs):
        print('Scan WiFi...')

        auth_mode_dict = {
            0: "open",
            1: "WEP",
            2: "WPA-PSK",
            3: "WPA2-PSK",
            4: "WPA/WPA2-PSK",
        }
        known_ssid = None
        for no in range(3):
            for info in self.station.scan():
                power_led.toggle()
                ssid, bssid, channel, RSSI, auth_mode, hidden = info
                auth_mode = auth_mode_dict.get(auth_mode, auth_mode)
                ssid = ssid.decode("UTF-8")
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
        power_led.flash(sleep=0.2, count=20)

    def _connect(self, ssid, password):
        status_dict = {
            network.STAT_IDLE: 'no connection and no activity',
            network.STAT_CONNECTING: 'connecting in progress',
            network.STAT_WRONG_PASSWORD: 'failed due to incorrect password',
            network.STAT_NO_AP_FOUND: 'failed because no access point replied',
            network.STAT_CONNECT_FAIL: 'failed due to other problems',
            network.STAT_GOT_IP: 'connection successful',
        }
        for no in range(0, 3):
            print('PHY mode:', network.phy_mode())
            # print('Connect to Wifi access point:', ssid, repr(password))
            print('Connect to Wifi access point:', ssid)
            power_led.toggle()
            self.station.connect(ssid, password)
            for wait_sec in range(30, 1, -1):
                status = self.station.status()
                status_text = status_dict[status]
                print(status_text)
                if status == network.STAT_GOT_IP:
                    # print('MAC:', self.station.config('mac'))
                    power_led.on()
                    return
                elif status == network.STAT_WRONG_PASSWORD:
                    return
                print('wait %i...' % wait_sec)
                power_led.flash(sleep=0.1, count=10)

            if self.station.isconnected():
                print('Connected to:', ssid)
                return
            else:
                print('Try again...')
                self.station.active(False)
                power_led.flash(sleep=0.1, count=20)
                power_led.off()
                self.station.active(True)

        print("ERROR: WiFi not connected! Password wrong?!?")
        power_led.flash(sleep=0.2, count=20)

    def __str__(self):
        return 'WiFi last refresh: %s - connected: %i - not connected: %i' % (
            self.last_refresh, self.is_connected_count, self.not_connected_count
        )


wifi = WiFi()

if __name__ == '__main__':
    print(wifi)
