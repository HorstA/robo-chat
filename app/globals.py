from pydantic import BaseModel


class Bots(BaseModel):
    leds: list


bots = Bots(leds=[])


def get_bots():
    return bots
