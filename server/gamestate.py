import json
import random
import threading

from commands.command import InfoRollDice, CommandEncoder


class GameState:
    lock = threading.Lock()

    def __init__(self, name):
        self.name = name
        self.last_dice_rolls = []

    def add_dice_roll(self, roll):
        self.lock.acquire()
        rolls = self.roll_dice(roll.amount, roll.sides)
        diffs = 0
        for i in range(len(rolls)):
            if isinstance(roll.rolled_against, int):
                if rolls[i] >= int(roll.rolled_against):
                    diffs = diffs + (rolls[i] - int(roll.rolled_against))
            else:
                if rolls[i] >= int(roll.rolled_against[i]):
                    diffs = diffs + (rolls[i] - int(roll.rolled_against[i]))

        roll = json.dumps(InfoRollDice(roll.character, rolls, roll.sides, roll.rolled_for, roll.rolled_against, (True if diffs < roll.equalizer else False), roll.dice_skins), cls=CommandEncoder)
        self.last_dice_rolls.append(roll)
        self.lock.release()
        return roll

    def roll_dice(self, amount, sides):
        results = []
        for i in range(amount):
            results.append(random.randrange(1, int(sides), 1))
        return results
