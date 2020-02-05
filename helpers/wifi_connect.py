"""
    Connect to WiFi via saved settings in:
        /_config_wifi.json
"""
import wifi
from context import Context

if __name__ == '__main__':
    context = Context()
    wifi.init(context)
