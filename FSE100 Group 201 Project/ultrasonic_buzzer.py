#!/usr/bin/env python3

import RPi.GPIO as GPIO
import time

# Define GPIO pins
TRIG = 11       # GPIO pin connected to Trig of Ultrasonic Sensor
ECHO = 12       # GPIO pin connected to Echo of Ultrasonic Sensor
BuzzerPin = 13  # GPIO pin connected to Buzzer

def setup():
    """ Setup the GPIO pins for the ultrasonic sensor and buzzer """
    GPIO.setmode(GPIO.BOARD)
    
    # Setup for ultrasonic sensor
    GPIO.setup(TRIG, GPIO.OUT)
    GPIO.setup(ECHO, GPIO.IN)
    
    # Setup for buzzer
    GPIO.setup(BuzzerPin, GPIO.OUT)
    GPIO.output(BuzzerPin, GPIO.HIGH)

def distance():
    """ Measure the distance using the ultrasonic sensor """
    GPIO.output(TRIG, 0)
    time.sleep(0.000002)
    GPIO.output(TRIG, 1)
    time.sleep(0.00001)
    GPIO.output(TRIG, 0)

    while GPIO.input(ECHO) == 0:
        pass
    time1 = time.time()
    
    while GPIO.input(ECHO) == 1:
        pass
    time2 = time.time()

    duration = time2 - time1
    return (duration * 340 / 2) * 100  # Convert to centimeters

def buzzer_on():
    """ Turn the buzzer on """
    GPIO.output(BuzzerPin, GPIO.LOW)

def buzzer_off():
    """ Turn the buzzer off """
    GPIO.output(BuzzerPin, GPIO.HIGH)

def beep(duration):
    """ Make the buzzer beep for a specified duration """
    buzzer_on()
    time.sleep(duration)
    buzzer_off()
    time.sleep(duration)

def loop():
    """ Main loop that checks the distance and controls the buzzer """
    while True:
        dis = distance()
        print(dis, 'cm')  # Print distance measurement

        if dis < 5:  # If the object is within 5 cm, buzz continuously
            buzzer_on()
        elif dis < 30:  # If within 30 cm, beep with decreasing interval
            beep_interval = (dis - 5) / 50.0  # Adjust beep interval
            beep(beep_interval)
        else:
            buzzer_off()  # Turn off buzzer if object is far
        
        time.sleep(0.3)

def destroy():
    """ Cleanup function to reset GPIO settings """
    GPIO.cleanup()

if __name__ == "__main__":
    setup()
    try:
        loop()
    except KeyboardInterrupt:
        destroy()