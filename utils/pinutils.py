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
        self.sleeping = False
        if platform.system() == "Linux":
            GPIO.setup(self.pin, GPIO.OUT)

    def _set_pin(self, color: str) -> int:
        match color.lower():
            case "red":
                self.pin = 13
            case "yellow":
                self.pin = 6
            case "green":
                self.pin = 5
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

            # print(f"LED {'an' if pin_value else 'aus'} ({self.color})")
            self.sleeping = True
            time.sleep(speed)
            self.sleeping = False
        print(f"LED blink aus ({self.color})")

    def blink(self, speed: int):
        if self.running:
            self.stop()
        t1 = threading.Thread(target=self._blink, args=(speed,))
        t1.daemon = True
        t1.start()

    def stop(self):
        self.running = False
        if platform.system() == "Linux":
            GPIO.output(self.pin, False)
        while self.sleeping:
            time.sleep(0.1)


class FakeBot(Led):
    def set_offline(self):
        self._status = "offline"
        self.stop()
        print(f"Bot {self.color} {self._status}")

    def set_idle(self):
        self._status = "idle"
        self.blink(1)
        print(f"Bot {self.color} {self._status}")

    def set_busy(self):
        self._status = "busy"
        self.blink(0.25)
        print(f"Bot {self.color} {self._status}")

    def get_status(self):
        return self._status


if __name__ == "__main__":
    GPIOHelper.init()
    red_bot = FakeBot("red")
    yellow_bot = FakeBot("yellow")
    green_bot = FakeBot("green")

    fake_bot = FakeBot("green")
    fake_bot.set_busy()

    # red_bot.blink(1)
    # yellow_bot.blink(0.75)
    # green_bot.blink(0.5)

    time.sleep(5)

    fake_bot.set_offline()
    # red_bot.stop()
    # yellow_bot.stop()
    # green_bot.stop()

    GPIOHelper.cleanup()
