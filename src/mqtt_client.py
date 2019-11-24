###########################################################################
#
# MQTT client firmware for Itead S20 Smart Socket
#
# Apache License Version 2.0
#
# Copyright (c) 2017, Tero Saarni
#
# Description
#
# Unofficial alternative firmware for Itead S20 Wifi Smart Socket based
# on MicroPython for ESP8266 http://micropython.org/ to control the socket
# remotely by MQTT protocol.
#
# The program registers with MQTT broker, subscribes topic and waits for
# message with 'on' or 'off' payload.  When message is received, the state
# of relay switch is set to on or off.
#
# If button is pressed on S20 Wifi Smart Socket, the program will publish
# 'on' or 'off' message to the broker.
#

from umqtt.simple import MQTTClient
import utime as time
import json
import micropython
import os

# try to recognize micropython on unix and load stub version of machine
if hasattr(os, 'uname'):
    from machine import Pin
else:
    from machine_stub import Pin



def get_value(pin):
    """get debounced value from pin by waiting for 20 msec for stable value"""
    cur_value = pin.value()
    stable = 0
    while stable < 20:
        if pin.value() == cur_value:
            stable = stable + 1
        else:
            stable = 0
            cur_value = pin.value()
    time.sleep_ms(1)
    return cur_value


class SmartSocket(object):

    def __init__(self, config):
        self.config = config
        self.relay = Pin(12, Pin.OUT)
        self.button = Pin(0, Pin.IN)
        self.button.irq(self.button_pressed)
        self.effective_button_value = 1 # the button is active-low
        self.mqtt = MQTTClient(client_id=self.config['mqtt']['client_id'],
                               server=self.config['mqtt']['server'],
                               user=self.config['mqtt']['user'],
                               password=self.config['mqtt']['password'])
        self.mqtt.set_callback(self.mqtt_action)


    def main_loop(self):
        self.mqtt_connect()
        while True:
            try:
                self.mqtt.wait_msg()
            except Exception as ex:
                print('Got excception {} retrying in 5 seconds'.format(ex))
                time.sleep(5)
                self.mqtt_connect()


    def button_pressed(self, pin):
        cur_button_value = get_value(pin)
        if cur_button_value == 1 and self.effective_button_value == 0:
            self.toggle_relay()
        self.effective_button_value = cur_button_value


    def toggle_relay(self):
        if self.relay.value() == 1:
            self.relay.off()
            self.mqtt.publish(self.config['mqtt']['feed'], b'off')
        else:
            self.relay.on()
            self.mqtt.publish(self.config['mqtt']['feed'], b'on')


    def mqtt_connect(self):
        self.mqtt.connect()
        self.mqtt.subscribe(self.config['mqtt']['feed'])


    def mqtt_action(self, topic, msg):
        print('Received {}: {}'.format(topic, msg))
        if msg == b'on':
            self.relay.on()
        elif msg == b'off':
            self.relay.off()
        elif msg == b'offon':
            self.relay.off()
            time.sleep(5)
            self.relay.on()



def main():
    #micropython.alloc_emergency_exception_buf(100)

    with open('config.json') as f:
        config = json.load(f)

    s = SmartSocket(config)
    s.main_loop()


if __name__ == '__main__':
    main()


###########################################################################
#
# References
#
# * MicroPython libraries
#   http://docs.micropython.org/en/latest/pyboard/library/index.html
#
# * umqtt
#   https://github.com/micropython/micropython-lib/tree/master/umqtt.simple
#
#
