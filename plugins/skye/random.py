"""
    Default random plugin
"""
import logging
from random import randint


class RandomPlugin(object):
    """ Tells the user the current date or time """

    def __init__(self, skye):
        self.skye = skye

    def roll_dice(self):
        logging.debug("Rolling a dice")
        roll = randint(1, 6)
        self.skye.speak(f"Rolled a {roll}")

    def flip_coin(self):
        logging.debug("Flipping a coin")
        flip = randint(1, 2)
        result = ("Tails" if flip == 1 else "Heads")
        self.skye.speak(f"The result is {result}")


def setup(skye):
    random_plugin = RandomPlugin(skye)
    skye.register_command(("roll", "dice", "roll a dice"),
                          random_plugin.roll_dice)
    skye.register_command(("flipacoin", "flip a coin", "flip"
                           "coin flip", "coin", "flip coin"),
                          random_plugin.flip_coin)
