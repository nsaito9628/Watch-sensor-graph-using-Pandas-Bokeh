#!/usr/bin/python
# -*- coding: utf-8 -*-
import json
import ssl
import time
import datetime 
import subprocess
import paho.mqtt.client as mqtt
import parameters as para



class Com:
    def __init__(self):
        self.client = para.client
        self.cacert = para.CACERT
        self.clientCert = para.CLIENTCERT
        self.clientKey = para.CLIENTKEY
        self.host = para.HOST
        self.port = para.PORT
    

    #Callback function when mqtt connection is successful
    def on_connect(self, client, userdata, flags, respons_code):
        #If the connection cannot be established, reboot after 90 seconds of waiting time for terminal access
        if respons_code != 0:
            print("respons_code:", respons_code, " flags:", flags)
            time.sleep(90)
            subprocess.call(["sudo","reboot"])
        print('Connected')


    #Function to determine the establishment of wifi connection
    def get_ssid(self):
        cmd = 'iwconfig wlan0|grep ESSID'
        r = subprocess.run(cmd, shell = True, stdout = subprocess.PIPE, stderr = subprocess.PIPE)\
            .stdout.decode().rstrip()
        idx = r.find('ESSID:')
        #If the connection cannot be established, reboot after 90 seconds of waiting time for terminal access
        if r[idx + 7:-1] == "ff/an":
            print("ESSID:", r[idx + 7:-1])
            time.sleep(90)
            subprocess.call(["sudo","reboot"])


    #Function that launches an MQTT client and creates an object instance
    def aws_connect(self):
        try:
            # certifications
            self.client.tls_set(
                self.cacert,
                certfile=self.clientCert,
                keyfile=self.clientKey,
                tls_version=ssl.PROTOCOL_TLSv1_2)
            self.client.tls_insecure_set(True)

            # callback
            self.client.on_connect = self.on_connect
            #client.on_disconnect = on_disconnect

            # port, keepalive
            self.client.connect(self.host, self.port, keepalive=60)

            self.client.loop_start()

        except KeyboardInterrupt:
            time.sleep(90)
            subprocess.call(["sudo","reboot"])


class Pub:
    def __init__(self):
        self.client = para.client
        self.topic_motion = para.TOPIC_SENSOR1
        self.topic_dust = para.TOPIC_DUST


    #Function that dispenses motion sensor data to the cloud at 0 seconds per minute
    def publish_motion(self, sub_t_countmotion, motion_count): 

        data = {}
        t = datetime.datetime.now()
        sub_t = str(t.minute/10)

        if sub_t[-1] != "0": 
            sub_t_countmotion = 0

        if (sub_t[-1] == "0") and sub_t_countmotion == 0:
            # IoTcoreへpublish
            data['Timestamp'] = int(time.time())
            data['DeleteTime'] = int((datetime.datetime.now() + datetime.timedelta(hours=96)).timestamp())
            data['motion_count'] = motion_count
            #print(data)
            self.client.publish(self.topic_motion, json.dumps(data, default=self.json_serial))  

            sub_t_countmotion = 1
            return True, sub_t_countmotion
            
        if (t.minute == 0 or sub_t[-1] == 0) and sub_t_countmotion == 1: 
            pass
            
        return False, sub_t_countmotion


    #Function that outputs dust sensor data to the cloud at 0 seconds per minute
    def publish_dust(self, sub_t_countdust, dust_count): 

        data = {}
        t = datetime.datetime.now()
        sub_t = str(t.minute/10)

        if sub_t[-1] != "0": 
            sub_t_countdust = 0

        if (sub_t[-1] == "0") and sub_t_countdust == 0:
            # IoTcoreへpublish
            data['Timestamp'] = int(time.time())
            data['DeleteTime'] = int((datetime.datetime.now() + datetime.timedelta(hours=96)).timestamp())
            data['dust_count'] = dust_count
            #print(data)
            self.client.publish(self.topic_dust, json.dumps(data, default=self.json_serial))  

            sub_t_countdust = 1
            return True, sub_t_countdust
            
        if (t.minute == 0 or sub_t[-1] == 0) and sub_t_countdust == 1: 
            pass
            
        return False, sub_t_countdust


    def json_serial(self, para):
        return para.isoformat()
