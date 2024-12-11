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

    def _blink(self, speed: float):
        self.running = True
        while True:
            if platform.system() == "Linux":
                GPIO.output(self.pin, not GPIO.input(self.pin) if self.running else False)
            print(f"LED {'an' if GPIO.input(self.pin) else 'aus'} ({self.color})")

            time.sleep(speed)

    def blink(self, speed: int):
       t1 = threading.Thread(target=self._blink, args=(speed,))
       t1.daemon = True
       t1.start()


    def stop(self):
        self.running = False
        print("Done")


if __name__ == "__main__":
    GPIOHelper.init()
    led = Led("green", 13)

    led.blink(1)
    time.sleep(4.7)
    led.stop()

    time.sleep(0.1)
    GPIOHelper.cleanup()
