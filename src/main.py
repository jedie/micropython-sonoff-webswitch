print('main.py')

import utime
utime.sleep(1)


def main():
    import gc
    gc.collect()

    import sys
    sys.modules.clear()

    from button_handler import Button
    from pins import Pins

    from wifi import WiFi

    __version__ = 'v0.8.1'

    # Init device button IRQ:
    Pins.button_pin.irq(Button().irq_handler)

    wifi = WiFi()
    wifi.ensure_connection()
    print('wifi: %s' % wifi)

    _RTC_KEY_RUN = 'run'
    _RUN_WEB_SERVER = 'web-server'

    from rtc import get_rtc_value
    if get_rtc_value(_RTC_KEY_RUN) == _RUN_WEB_SERVER:
        print('start webserver')

        from rtc import update_rtc_dict
        update_rtc_dict(data={_RTC_KEY_RUN: None})  # run OTA client on next boot

        del update_rtc_dict
        del get_rtc_value
        del sys.modules['rtc']
        del Pins
        del sys.modules['pins']
        gc.collect()

        from webswitch import WebServer  # noqa isort:skip
        from watchdog import Watchdog  # noqa isort:skip
        from power_timer import PowerTimer  # noqa isort:skip

        power_timer = PowerTimer()
        power_timer.schedule_next_switch()

        gc.collect()
        WebServer(
            power_timer=power_timer,
            watchdog=Watchdog(
                wifi=wifi,
                check_callback=power_timer.schedule_next_switch
            ),
            version=__version__
        ).run()
    else:
        print('start OTA')
        Pins.power_led.off()
        from rtc import update_rtc_dict
        update_rtc_dict(data={_RTC_KEY_RUN: _RUN_WEB_SERVER})  # run web server on next boot
        from ota_client import OtaUpdate

        gc.collect()
        OtaUpdate().run()

    from reset import ResetDevice
    ResetDevice(reason='unknown').reset()


main()
