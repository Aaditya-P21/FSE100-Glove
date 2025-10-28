#!/usr/bin/env python3

import RPi.GPIO as GPIO
import time
import subprocess
import os
import glob

# --- Constants ---
# Ultrasonic sensor pins
TRIG = 11
ECHO = 12

# Buzzer pin
BUZZER_PIN = 13  # You can change this if needed

# --- Setup Functions ---

def setup_ultrasonic():
    GPIO.setmode(GPIO.BOARD)  # Set pin numbering to BOARD (physical pin number)
    GPIO.setup(TRIG, GPIO.OUT)
    GPIO.setup(ECHO, GPIO.IN)

def setup_buzzer():
    GPIO.setmode(GPIO.BOARD)  # Set pin numbering to BOARD (physical pin number)
    GPIO.setup(BUZZER_PIN, GPIO.OUT)
    GPIO.output(BUZZER_PIN, GPIO.HIGH)

# --- Ultrasonic Distance Sensor ---

def get_distance():
    # Send a pulse to TRIG
    GPIO.output(TRIG, False)  # Make sure TRIG is LOW initially
    time.sleep(0.000002)  # Small delay to ensure it's off
    GPIO.output(TRIG, True)  # Send a HIGH pulse
    time.sleep(0.00001)  # Pulse duration
    GPIO.output(TRIG, False)  # End pulse
    
    # Record the start time
    while GPIO.input(ECHO) == 0:
        start = time.time()

    # Record the end time
    while GPIO.input(ECHO) == 1:
        end = time.time()

    # Calculate the duration of the pulse
    duration = end - start
    
    # Calculate distance in cm using the formula:
    # Distance = (Duration * Speed of sound in air) / 2
    # Speed of sound is roughly 340 meters/second (or 0.034 cm/µs)
    distance_cm = duration * 34000 / 2
    
    return distance_cm

# --- Temperature Sensor ---

def init_temp_sensor():
    os.system('modprobe w1-gpio')
    os.system('modprobe w1-therm')

def get_temp_paths():
    base_dir = '/sys/bus/w1/devices/'
    devices = glob.glob(base_dir + '28*')
    if not devices:
        print("Temperature sensor not found!")
        return None
    return devices[0] + '/w1_slave'

def read_temp_raw(device_file):
    with open(device_file, 'r') as f:
        return f.readlines()

def read_temperature(device_file):
    lines = read_temp_raw(device_file)
    while lines[0].strip()[-3:] != 'YES':
        time.sleep(0.2)
        lines = read_temp_raw(device_file)
    equals_pos = lines[1].find('t=')
    if equals_pos != -1:
        temp_string = lines[1][equals_pos+2:]
        temp_c = float(temp_string) / 1000.0
        temp_f = temp_c * 9.0 / 5.0 + 32.0
        return temp_c, temp_f
    return None, None

# --- Buzzer ---

def buzzer_on():
    GPIO.output(BUZZER_PIN, GPIO.LOW)

def buzzer_off():
    GPIO.output(BUZZER_PIN, GPIO.HIGH)

def buzzer_beep(duration=0.5):
    buzzer_on()
    time.sleep(duration)
    buzzer_off()

# --- Text to Speech ---

def speak(text):
    subprocess.run(["espeak", text])

# --- Main Function ---

def main():
    print("Starting Raspberry Pi Sensor Suite...")

    # Initialize
    setup_ultrasonic()
    setup_buzzer()
    init_temp_sensor()
    temp_file = get_temp_paths()

    try:
        while True:
            # Get distance from the ultrasonic sensor
            dist = get_distance()
            print(f"Distance: {dist:.2f} cm")
            speak(f"Object is {dist:.1f} centimeters away")

            # Check if the distance is too short and beep the buzzer
            if dist < 20:
                buzzer_beep(0.1)
            else:
                buzzer_off()

            # Get temperature data
            if temp_file:
                temp_c, temp_f = read_temperature(temp_file)
                if temp_c is not None:
                    print(f"Temperature: {temp_c:.2f} °C / {temp_f:.2f} °F")
                    speak(f"The temperature is {temp_c:.1f} degrees Celsius")
            else:
                print("Skipping temperature read: No sensor found.")

            # Add a short delay before the next reading
            time.sleep(1)

    except KeyboardInterrupt:
        print("\nProgram stopped by user.")
    finally:
        GPIO.cleanup()

# --- Run Main ---
if __name__ == "__main__":
    main()
