import time

import platform

print(platform.system())

led_pin = 13
wait_seconds = 1
running = True

if platform.system() == 'Linux':
    import RPi.GPIO as GPIO
    # GPIO.setmode(GPIO.BOARD)
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(led_pin, GPIO.OUT)

try:
    while running:
        print("LED an")
        if platform.system() == 'Linux':
            GPIO.output(led_pin, True)
        time.sleep(wait_seconds)

        print("LED aus")
        if platform.system() == 'Linux':
            GPIO.output(led_pin, False)
        time.sleep(wait_seconds)
except KeyboardInterrupt:
    if platform.system() == 'Linux':
        GPIO.cleanup()
    running = False
