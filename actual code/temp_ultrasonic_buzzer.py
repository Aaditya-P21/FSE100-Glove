#!/usr/bin/env python3

import RPi.GPIO as GPIO
import time
import os
import subprocess

# Define GPIO pins
TRIG = 11       # GPIO pin connected to Trig of Ultrasonic Sensor
ECHO = 12       # GPIO pin connected to Echo of Ultrasonic Sensor
BuzzerPin = 13  # GPIO pin connected to Buzzer

# Temperature threshold
TEMP_THRESHOLD = 27.0

# DS18B20 sensor ID
ds18b20 = ''

# Temperature warning flag
temp_warning_active = False
last_warning_time = 0
WARNING_INTERVAL = 10  # Seconds between warnings

def setup():
    """ Setup the GPIO pins and DS18B20 sensor """
    global ds18b20
    
    # Setup GPIO
    GPIO.setmode(GPIO.BOARD)
    
    # Setup for ultrasonic sensor
    GPIO.setup(TRIG, GPIO.OUT)
    GPIO.setup(ECHO, GPIO.IN)
    
    # Setup for buzzer
    GPIO.setup(BuzzerPin, GPIO.OUT)
    GPIO.output(BuzzerPin, GPIO.HIGH)
    
    # Setup DS18B20 temperature sensor
    for i in os.listdir('/sys/bus/w1/devices'):
        if i != 'w1_bus_master1':
            ds18b20 = i  # Use the first DS18B20 device found
            print(f"DS18B20 sensor found: {ds18b20}")
            break

def read_temperature():
    """ Read temperature from DS18B20 sensor """
    global ds18b20
    try:
        location = '/sys/bus/w1/devices/' + ds18b20 + '/w1_slave'
        tfile = open(location)
        text = tfile.read()
        tfile.close()
        secondline = text.split("\n")[1]
        temperaturedata = secondline.split(" ")[9]
        temperature = float(temperaturedata[2:])
        temperature = temperature / 1000
        return temperature
    except:
        return None

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

def speak_warning(message):
    """ Use espeak to announce warning message """
    try:
        subprocess.Popen(['espeak', message], 
                        stdout=subprocess.DEVNULL, 
                        stderr=subprocess.DEVNULL)
    except Exception as e:
        print(f"Error with espeak: {e}")

def check_temperature():
    """ Check temperature and issue warning if threshold exceeded """
    global temp_warning_active, last_warning_time
    
    temp = read_temperature()
    if temp is not None:
        print(f"Current temperature: {temp:.3f} C")
        
        # Check if temperature exceeds threshold
        if temp > TEMP_THRESHOLD:
            current_time = time.time()
            # Only announce warning every WARNING_INTERVAL seconds
            if current_time - last_warning_time >= WARNING_INTERVAL:
                warning_msg = f"Warning! High temperature detected. Current temperature is {temp:.1f} degrees celsius"
                print(warning_msg)
                speak_warning(warning_msg)
                last_warning_time = current_time
                temp_warning_active = True
        else:
            temp_warning_active = False
    
    return temp

def loop():
    """ Main loop that monitors temperature and distance """
    while True:
        # Check temperature
        check_temperature()
        
        # Measure distance
        dis = distance()
        print(f"Distance: {dis:.2f} cm")
        
        # Control buzzer based on distance
        if dis < 5:  # Within 5 cm - continuous beep
            print("Object very close! Continuous beeping...")
            buzzer_on()
            time.sleep(0.3)
        elif dis < 30:  # Within 30 cm - beep with decreasing interval
            # Calculate beep interval (slower beep as object gets farther)
            beep_interval = (dis - 5) / 100.0  # Interval between 0 and 0.25 seconds
            print(f"Object detected! Beeping with interval: {beep_interval:.3f}s")
            beep(beep_interval)
            time.sleep(0.1)
        else:  # Beyond 30 cm - no beep
            buzzer_off()
            time.sleep(0.3)
        
        print("")  # Empty line for readability

def destroy():
    """ Cleanup function to reset GPIO settings """
    buzzer_off()
    GPIO.cleanup()
    print("\nProgram terminated. GPIO cleaned up.")

if __name__ == "__main__":
    try:
        print("Starting Temperature and Ultrasonic Sensor Monitor...")
        print(f"Temperature threshold: {TEMP_THRESHOLD} C")
        print("Buzzer behavior:")
        print("  - Continuous beep: distance < 5 cm")
        print("  - Interval beep: distance < 30 cm")
        print("  - No beep: distance >= 30 cm")
        print("\nPress Ctrl+C to stop\n")
        
        setup()
        loop()
    except KeyboardInterrupt:
        destroy()
