import json

from dice.dice import decode_dice, DiceEncoder


class DiceGroup:
    def __init__(self, name, dice, image_path):
        self.name = name
        self.dice = dice
        self.image_path = image_path


def decode_dice_group(dct):
    if dct['class'] == "dice_group":
        decoded_dice = []
        for dice in dct['dice']:
            decoded_dice.append(json.loads(dice, object_hook=decode_dice))
        return DiceGroup(dct['name'], decoded_dice, dct['image_path'])
    return dct


class DiceGroupEncoder(json.JSONEncoder):

    def default(self, d):
        if isinstance(d, DiceGroup):
            encoded_dice = []
            for dice in d.dice:
                encoded_dice.append(json.dumps(dice, cls=DiceEncoder))
            return {"class": 'dice_group', "name": d.name, "dice": encoded_dice, "image_path": str(d.image_path)}
        else:
            return super().default(d)
