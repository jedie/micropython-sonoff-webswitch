"""
    Force start OTA update client.
    This is normally not needed, see main.py
"""


if __name__ == '__main__':
    print('Start OTA update')
    import sys
    sys.modules.clear()

    import gc
    gc.collect()

    from ota_client import OtaUpdate

    OtaUpdate().run()

    print('Hard reset device...')
    import machine
    import utime as time
    time.sleep(1)
    machine.reset()
    time.sleep(1)
    sys.exit()
