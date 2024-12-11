import time

import platform
if platform.system() == 'Linux':
    import RPi.GPIO as GPIO


class GPIOHelper:
    @staticmethod
    def init():
        print(platform.system())
        if platform.system() == "Linux":
            GPIO.setmode(GPIO.BCM)

    @staticmethod
    def cleanup():
        if platform.system() == "Linux":
            GPIO.cleanup()


print(platform.system())

led_pin = 13
wait_seconds = 1
running = True

GPIOHelper.init()

if platform.system() == 'Linux':
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
    print("cleanup")
    running = False
    GPIOHelper.cleanup()
