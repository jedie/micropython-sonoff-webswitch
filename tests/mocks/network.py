
STA_IF = 'STA_IF'  # WiFi station interface
AP_IF = 'AP_IF'  # access point interface'


class WLAN:
    def __init__(self, station):
        self._station = station
        assert station == STA_IF or station == AP_IF

    def disconnect(self):
        print(f' *** mock call: network.WLAN({self._station}).disconnect()')
