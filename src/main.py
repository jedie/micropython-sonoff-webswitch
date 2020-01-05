

__version__ = 'v0.11.0'


def main():

    import sys
    sys.modules.clear()

    from button_handler import Button
    from pins import Pins

    # Init device button IRQ:
    Pins.button_pin.irq(Button().irq_handler)

    from context import Context

    context = Context

    import wifi
    wifi.init(context)
    del sys.modules['wifi']

    _RTC_KEY_RUN = 'run'
    _RUN_WEB_SERVER = 'web-server'
    _RUN_SOFT_OTA = 'soft-ota'

    from rtc import get_rtc_value
    if get_rtc_value(_RTC_KEY_RUN) == _RUN_WEB_SERVER:
        print('start webserver')

        from rtc import update_rtc_dict
        update_rtc_dict(data={_RTC_KEY_RUN: _RUN_SOFT_OTA})  # run OTA client on next boot

        del update_rtc_dict
        del get_rtc_value
        del sys.modules['rtc']

        # init Watchdog timer
        from watchdog import Watchdog
        context.watchdog = Watchdog(context)

        from webswitch import WebServer

        WebServer(context=context, version=__version__).run()
    else:
        print('start "soft" OTA')
        Pins.power_led.off()
        from rtc import update_rtc_dict
        update_rtc_dict(data={_RTC_KEY_RUN: _RUN_WEB_SERVER})  # run web server on next boot
        from ota_client import OtaUpdate

        OtaUpdate().run()

    from reset import ResetDevice
    ResetDevice(reason='unknown').reset()


if __name__ == '__main__':
    import utime
    for no in range(2, 0, -1):
        print('%i main.py wait...' % no)
        utime.sleep(1)
    main()
