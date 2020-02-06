"""
    Start "soft" OTA update client.
    This is normally not needed, see main.py
"""


if __name__ == '__main__':
    print('Start "soft" OTA update')
    import sys
    sys.modules.clear()

    import gc
    gc.collect()

    from rtc import update_rtc_dict
    update_rtc_dict(data={'run': 'web-server'})  # run web server on next boot

    import sys
    sys.modules.clear()

    import gc
    gc.collect()

    from ota_client import SoftOtaUpdate
    SoftOtaUpdate().run()
