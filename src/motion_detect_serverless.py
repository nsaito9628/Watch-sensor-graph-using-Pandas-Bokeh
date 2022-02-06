#!/usr/bin/python
# -*- coding: utf-8 -*-
import time
import sys
from awsMQTTconnect import Com, Pub
from sensing import Sensor


senser = Sensor()
com = Com()
pub = Pub()


def loop():
    sub_t_countmotion = 0
    motion_count = 0

    while True:
        motion_count = senser.motion_count(motion_count)

        bool, sub_t_countmotion = pub.publish_motion(sub_t_countmotion, motion_count)

        if bool == True: motion_count = 0

        time.sleep(1)


if __name__ == '__main__':
    try:
        time.sleep(90)

        #wifi connection confirmation and MQTT connection
        com.get_ssid()
        com.aws_connect()

        #Main loop execution
        loop()

    except KeyboardInterrupt:
        sys.exit()
