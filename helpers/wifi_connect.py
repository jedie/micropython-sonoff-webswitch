import network
from wifi_connect import connect

if __name__ == '__main__':
    # Connect or reconnect
    sta_if = network.WLAN(network.STA_IF)
    sta_if.disconnect()
    connect(station=sta_if)
    print('connected:', sta_if.isconnected())
