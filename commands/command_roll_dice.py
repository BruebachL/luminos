import json


class CommandRollDice:

    def __init__(self, character, amount, sides, rolled_for, rolled_against, equalizer, dice_skins):
        self.character = character
        self.amount = amount
        self.sides = sides
        self.rolled_for = rolled_for
        self.rolled_against = rolled_against
        self.equalizer = equalizer
        self.dice_skins = dice_skins


def decode_command_roll_dice(dct):
    if dct['class'] == "command_roll_dice":
        return CommandRollDice(dct['character'], dct['amount'], dct['sides'], dct['rolled_for'], dct['rolled_against'], dct['equalizer'], dct['dice_skins'])
    return dct


class CommandRollDiceEncoder(json.JSONEncoder):

    def default(self, r):
        if isinstance(r, CommandRollDice):
            return {"class": 'command_roll_dice', "character": r.character, "amount": r.amount, "sides": r.sides, "rolled_for": r.rolled_for, "rolled_against": r.rolled_against, "equalizer": r.equalizer, "dice_skins": r.dice_skins}
        else:
            return super().default(r)
