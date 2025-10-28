#!/usr/bin/env python3

import RPi.GPIO as GPIO
import time
import subprocess

# GPIO Pins for Ultrasonic Sensor
TRIG = 11
ECHO = 12

def setup():
    # Set up the GPIO mode and pins
    GPIO.setmode(GPIO.BOARD)
    GPIO.setup(TRIG, GPIO.OUT)
    GPIO.setup(ECHO, GPIO.IN)

def speak(text):
    text = text.replace(" ", "_") # Replace spaces with underscores to prevent parsing issues
    subprocess.run(("espeak \"" + text + "\" 2>/dev/null").split(" ")) # Construct the command and split into tokens for subprocess.run

def distance():
    # Ensure trigger is low
    GPIO.output(TRIG, 0)
    time.sleep(0.000002)
    
    # Send a 10 microsecond pulse to trigger the sensor
    GPIO.output(TRIG, 1)
    time.sleep(0.00001)
    GPIO.output(TRIG, 0)
    
    # Wait for the echo to start
    while GPIO.input(ECHO) == 0:
        start_time = time.time()
    
    # Wait for the echo to end
    while GPIO.input(ECHO) == 1:
        end_time = time.time()
    
    duration = end_time - start_time
    # Calculate distance: (duration * speed of sound (340 m/s) / 2) * 100 to convert to cm
    return duration * 340 / 2 * 100

def loop():
    """
    Main loop to measure distance and speak the result every 3 seconds.
    """
    while True:
        dis = distance()
        # Print distance in centimeters with 2 decimal places
        print(f"{dis:.2f} cm")
        # Construct the message for text-to-speech
        speak_message = f"Distance is {dis:.2f} centimeters"
        # Use TTS to speak the message
        speak(speak_message)
        # Wait for 3 seconds before taking the next reading
        time.sleep(3)

def destroy():
    GPIO.cleanup()

if __name__ == "__main__":
    setup()
    try:
        loop()
    except KeyboardInterrupt:
        destroy()

