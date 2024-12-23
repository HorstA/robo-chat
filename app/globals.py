from utils.pinutils import FakeBot


class Bots:
    def __init__(self, leds: list[FakeBot]):
        self.leds = leds


bots = Bots([FakeBot("red"), FakeBot("yellow"), FakeBot("green")])


def get_bots():
    return bots
