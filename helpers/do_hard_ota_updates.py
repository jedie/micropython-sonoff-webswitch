"""
    Start "hard" OTA updates
"""

import machine

if __name__ == '__main__':
    print('Force hard-OTA via yaota8266')
    machine.RTC().memory('yaotaota')
    machine.reset()
