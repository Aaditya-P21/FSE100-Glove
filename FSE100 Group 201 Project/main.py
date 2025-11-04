#!/usr/bin/env python3
"""
main.py – Integration of temperature sensor (DS18B20) and ultrasonic distance + buzzer.
Runs both loops in separate threads.
"""

import threading
import time
import sys
import signal

# Import the two modules (make sure the files are named exactly as below)
import Temp_Sensor as temp_mod
import ultrasonic_buzzer as ultra_mod


# ----------------------------------------------------------------------
# Global flag to signal threads to stop on Ctrl+C
# ----------------------------------------------------------------------
stop_event = threading.Event()


def signal_handler(sig, frame):
    """Handle Ctrl+C gracefully."""
    print("\n[main] Shutting down...")
    stop_event.set()
    # Give a moment for threads to exit cleanly
    time.sleep(0.5)
    sys.exit(0)


# ----------------------------------------------------------------------
# Temperature thread – wraps Temp_Sensor.loop()
# ----------------------------------------------------------------------
def temperature_thread():
    try:
        temp_mod.setup()
        warning_given = False

        while not stop_event.is_set():
            temp = temp_mod.read()
            print(f"[Temp] Current temperature: {temp:.2f} °C")

            if temp >= 28.0 and not warning_given:
                temp_mod.speak("Warning temperature above twenty eight degrees")
                warning_given = True
            elif temp >= 28.0 and warning_given:
                temp_mod.speak("Warning")
            elif temp < 28.0 and warning_given:
                warning_given = False

            time.sleep(1)

    except Exception as e:
        print(f"[Temp] Error: {e}")
    finally:
        temp_mod.destroy()
        print("[Temp] Thread terminated.")


# ----------------------------------------------------------------------
# Ultrasonic + buzzer thread – wraps Ultrasonic_buzzer.loop()
# ----------------------------------------------------------------------
def ultrasonic_thread():
    try:
        ultra_mod.setup()

        while not stop_event.is_set():
            dis = ultra_mod.distance()
            print(f"[Ultra] Distance: {dis:.1f} cm")

            if dis < 5:                     # < 5 cm → continuous buzz
                ultra_mod.buzzer_on()
            elif dis < 30:                  # 5-30 cm → beeping
                beep_interval = (dis - 5) / 50.0
                ultra_mod.beep(beep_interval)
            else:                           # > 30 cm → off
                ultra_mod.buzzer_off()

            time.sleep(0.3)

    except Exception as e:
        print(f"[Ultra] Error: {e}")
    finally:
        ultra_mod.destroy()
        print("[Ultra] Thread terminated.")


# ----------------------------------------------------------------------
# Main entry point
# ----------------------------------------------------------------------
def main():
    # Register signal handler for graceful shutdown
    signal.signal(signal.SIGINT, signal_handler)

    print("[main] Starting sensors...")

    # Create and start threads
    t_temp = threading.Thread(target=temperature_thread, daemon=True)
    t_ultra = threading.Thread(target=ultrasonic_thread, daemon=True)

    t_temp.start()
    t_ultra.start()

    # Keep main thread alive until stop_event is set
    try:
        while not stop_event.is_set():
            time.sleep(0.1)
    except KeyboardInterrupt:
        pass  # Already handled by signal_handler

    # Wait for threads to finish (they will exit quickly because of stop_event)
    t_temp.join(timeout=1)
    t_ultra.join(timeout=1)

    print("[main] All done.")


if __name__ == "__main__":
    main()