import threading
import time
import platform

if platform.system() == "Linux":
    import RPi.GPIO as GPIO  # type: ignore


def only_linux(func):
    def wrapper(*args, **kwargs):
        if platform.system() == "Linux":
            return func(*args, **kwargs)

    return wrapper


class GPIOHelper:
    @staticmethod
    @only_linux
    def init():
        GPIO.setmode(GPIO.BCM)

    @staticmethod
    @only_linux
    def cleanup():
        GPIO.cleanup()


class Led:
    def __init__(self, color: str):
        self.color = color
        self._set_pin(color)
        self.running = False
        if platform.system() == "Linux":
            GPIO.setup(self.pin, GPIO.OUT)

    def _set_pin(self, color: str) -> int:
        match color.lower():
            case "red":
                self.pin = 5
            case "yellow":
                self.pin = 6
            case "green":
                self.pin = 13
            case _:
                raise ValueError("falsche Farbe.")

    def _blink(self, speed: float):
        self.running = True
        pin_value = False
        while self.running:
            if platform.system() == "Linux":
                pin_value = not GPIO.input(self.pin) if self.running else False
                GPIO.output(self.pin, pin_value)
            else:
                # fake it
                pin_value = not pin_value if self.running else False

            print(f"LED {'an' if pin_value else 'aus'} ({self.color})")

            time.sleep(speed)
        print(f"LED blink aus ({self.color})")

    def blink(self, speed: int):
        t1 = threading.Thread(target=self._blink, args=(speed,))
        t1.daemon = True
        t1.start()

    def stop(self):
        self.running = False
        if platform.system() == "Linux":
            GPIO.output(self.pin, False)


if __name__ == "__main__":
    GPIOHelper.init()
    red_bot = Led("red")
    yellow_bot = Led("yellow")
    green_bot = Led("green")

    red_bot.blink(1)
    yellow_bot.blink(0.75)
    green_bot.blink(0.5)

    time.sleep(15)

    red_bot.stop()
    yellow_bot.stop()
    green_bot.stop()

    GPIOHelper.cleanup()
