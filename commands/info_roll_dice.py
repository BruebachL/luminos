import json


class InfoRollDice:

    def __init__(self, player, roll_value, dice_used, rolled_for, rolled_against, success, dice_skins):
        self.player = player
        self.roll_value = roll_value
        self.dice_used = dice_used
        self.rolled_for = rolled_for
        self.rolled_against = rolled_against
        self.success = success
        self.dice_skins = dice_skins

    def __str__(self):
        return str(self.player) + " rolled a " + str(self.roll_value) + " with a D" + str(self.dice_used) + " to check " + str(self.rolled_for) + ". Their value is at " + str(self.rolled_against) + (" They succeeded." if self.success else " They failed.")


def decode_info_roll_dice(dct):
    if dct['class'] == "info_roll_dice":
        return InfoRollDice(dct['player'], dct['roll_value'], dct['dice_used'], dct['rolled_for'], dct['rolled_against'], dct['success'], dct['dice_skins'])
    return dct


class InfoRollDiceEncoder(json.JSONEncoder):

    def default(self, i):
        if isinstance(i, InfoRollDice):
            return {"class": 'info_roll_dice', "player": i.player, "roll_value": i.roll_value, "dice_used": i.dice_used, "rolled_for": i.rolled_for, "rolled_against": i.rolled_against, "success": i.success, "dice_skins": i.dice_skins}
        else:
            return super().default(i)
