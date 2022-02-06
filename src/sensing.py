#!/usr/bin/python
# -*- coding: utf-8 -*-
#import wiringpi as pi
import RPi.GPIO as GPIO
import time
import parameters as para


class Sensor:
    def __init__(self):
        self.motion_pin = para.MOTION_PIN #Motion sensor signal port : GPIO 21
        self.dust_PIN = para.DUST_PIN #Dust sensor signal port：GPIO 15
        self.sensor_no = para.SENSOR_NO
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self.motion_pin, GPIO.IN)
        GPIO.setup(self.dust_PIN, GPIO.IN)
       

    #Output sensor HI / LO at 1/0
    def motion_detect(self): 

        if self.sensor_no == 1:
            if GPIO.input(self.motion_pin) == GPIO.HIGH:
                sig = 0
            else:
                sig = 1

        return sig


    #If the sensor has HI output, increment the counter
    def motion_count(self, motion_count):
        
        motion_sig = self.motion_detect()
        
        if motion_sig == 1:
            motion_count = motion_count + 1

        return motion_count


    #Measured when the dust sensor is HIGH or LOW 
    def pulseIn(self, start=1, end=0):
        if start==0: end = 1
        t_start = 0
        t_end = 0
        # Measure the time when ECHO_PIN is HIGH
        while  GPIO.input(self.dust_PIN) == end:
            i= GPIO.input(self.dust_PIN)
            t_start = time.time()            
        while  GPIO.input(self.dust_PIN) == start:
            i=GPIO.input(self.dust_PIN)
            t_end = time.time()

        return t_end - t_start


    # Convert unit to microgram / m ^ 3
    def pcs2ugm3(self, pcs):
        pi = 3.14159
        #Whole grain density
        density = 1.65 * pow (10, 12)
        #Radius of PM2.5 particles
        r25 = 0.44 * pow (10, -6)
        vol25 = (4/3) * pi * pow (r25, 3)
        mass25 = density * vol25
        K = 3531.5 # per m^3
        return pcs * K * mass25


    # pm2.5 measurement
    def get_pm25(self):
        t0 = time.time()
        t = 0
        ts = 30 #Sampling time
        while True:
            # Find the time t in the LOW state
            dt = self.pulseIn(0)
            if dt<1: t = t + dt
            
            if ((time.time() - t0) > ts):
                # Percentage of LOW [0-100%]
                ratio = (100*t)/ts
                #Calculate dust concentration
                concent = 1.1 * pow(ratio,3) - 3.8 * pow(ratio,2) + 520 * ratio + 0.62         
                dust_count = self.pcs2ugm3(concent)
                #print(dust_count)
                if dust_count < 0: dust_count = 0 
                return dust_count
