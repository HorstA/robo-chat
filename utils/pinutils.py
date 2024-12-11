import asyncio
import time
import platform

if platform.system() == "Linux":
    import RPi.GPIO as GPIO

    GPIO.setmode(GPIO.BCM)

print(platform.system())


class Led:
    def __init__(self, color: str, pin: int):
        self.color = color
        self.pin = pin
        self.running = False
        if platform.system() == "Linux":
            GPIO.setup(pin, GPIO.OUT)

    async def _blink(self, speed: int, stop_event: asyncio.Event):
        self.running = True
        if speed == 0:
            wait_seconds = 1
        else:
            wait_seconds = 0.5
        while not stop_event.is_set():
            print(f"LED an ({self.color})")
            if platform.system() == "Linux":
                GPIO.output(self.pin, True)
            await asyncio.sleep(wait_seconds)

            print("LED aus")
            if platform.system() == "Linux":
                GPIO.output(self.pin, False)
            await asyncio.sleep(wait_seconds)

    def blink(self, speed: int):
        # asyncio.run(self._blink(speed))
        self.stop_event = asyncio.Event()
        self.task = asyncio.create_task(self._blink(speed, self.stop_event))

    async def stop(self):
        self.stop_event.set()  # Set the event to stop the background_task
        await self.task  # Await the task to complete

        print("Done")
        # self.running = False


async def main():
    green = Led("green", 13)
    red = Led("red", 13)

    green.blink(0)
    await asyncio.sleep(5)
    await green.stop()
    red.blink(1)
    await asyncio.sleep(5)
    await red.stop()
    green.blink(0)
    await asyncio.sleep(5)
    await green.stop()

    if platform.system() == "Linux":
        GPIO.cleanup()


async def stop(led):
    await led.stop()


if __name__ == "__main__":
    # led = Led("green", 13)

    # led.blink(0)
    # time.sleep(5)
    # led.stop()
    # # asyncio.run(stop())

    # if platform.system() == "Linux":
    #     GPIO.cleanup()

    asyncio.run(main())
    # greeLed = Led("green", 13)

    # greeLed.blink(0)
    # time.sleep(5)
    # greeLed.stop()

    # if platform.system() == 'Linux':
    #     GPIO.cleanup()


### TODO


# import asyncio

# async def background_task(stop_event):
#     while not stop_event.is_set():
#         print('doing something')
#         await asyncio.sleep(1)

# async def main():
#     stop_event = asyncio.Event()
#     task = asyncio.create_task(background_task(stop_event))
#     # Simulate running the task for some time
#     await asyncio.sleep(5)
#     stop_event.set() # Set the event to stop the background_task
#     await task # Await the task to complete
#     print('Done!')

# asyncio.run(main())


# led_pin = 13
# wait_seconds = 1
# running = True

# if platform.system() == 'Linux':
#     # GPIO.setmode(GPIO.BOARD)
#     GPIO.setmode(GPIO.BCM)
#     GPIO.setup(led_pin, GPIO.OUT)

# try:
#     while running:
#         print("LED an")
#         if platform.system() == 'Linux':
#             GPIO.output(led_pin, True)
#         time.sleep(wait_seconds)

#         print("LED aus")
#         if platform.system() == 'Linux':
#             GPIO.output(led_pin, False)
#         time.sleep(wait_seconds)
# except KeyboardInterrupt:
#     if platform.system() == 'Linux':
#         GPIO.cleanup()
#     running = False
