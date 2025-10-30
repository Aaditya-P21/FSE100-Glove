#!/usr/bin/env python3
import os
import subprocess
import time

ds18b20 = ''

def setup():
    global ds18b20
    for i in os.listdir('/sys/bus/w1/devices'):
        if i != 'w1_bus_master1':
            ds18b20 = '28-01204bd4f5ce'

def read():
#   global ds18b20
    location = '/sys/bus/w1/devices/' + ds18b20 + '/w1_slave'
    tfile = open(location)
    text = tfile.read()
    tfile.close()
    secondline = text.split("\n")[1]
    temperaturedata = secondline.split(" ")[9]
    temperature = float(temperaturedata[2:])
    temperature = temperature / 1000
    return temperature

def loop():
    while True:
        if read() != None:
            print ("Current temperature : %0.2f C" % read())
            if read() >= 27.0:
                speak(Too Hot!)

def destroy():
    pass

def speak(text):
    text = text.replace(" ", "_")  # Replace spaces with underscores to prevent parsing issues
    subprocess.run((
        "espeak \"" + text + "\" 2>/dev/null"
    ).split(" "))  # Construct the command and split into tokens for subprocess.run

if __name__ == '__main__':
    try:
        setup()
        loop()
    except KeyboardInterrupt:
        destroy()

