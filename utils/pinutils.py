import threading
import time
import platform

if platform.system() == "Linux":
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


class Led:
    def __init__(self, color: str, pin: int):
        self.color = color
        self.pin = pin
        self.running = False
        if platform.system() == "Linux":
            GPIO.setup(pin, GPIO.OUT)

    def _blink(self, speed: int):
        self.running = True
        if speed == 0:
            wait_seconds = 1
        else:
            wait_seconds = 0.5
        while self.running:
            print(f"LED an ({self.color})")
            if platform.system() == "Linux":
                GPIO.output(self.pin, True)
            time.sleep(wait_seconds)

            print("LED aus")
            if platform.system() == "Linux":
                GPIO.output(self.pin, False)
            time.sleep(wait_seconds)

    def blink(self, speed: int):
        threading.Thread(target=self._blink, args=(speed,)).start()

    def stop(self):
        self.running = False
        print("Done")


if __name__ == "__main__":
    GPIOHelper.init()

    led = Led("green", 13)

    led.blink(0)
    time.sleep(5)
    led.stop()

    GPIOHelper.cleanup()
