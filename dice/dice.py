import json


class Dice:
    def __init__(self, name, group, image_path, use):
        self.name = name
        self.group = group
        if isinstance(image_path, str):
            self.image_path = image_path
        else:
            self.image_path = str(image_path)
        self.use = use


def decode_dice(dct):
    if dct['class'] == "dice":
        return Dice(dct['name'], dct['group'], dct['image_path'], dct['use'])
    return dct


class DiceEncoder(json.JSONEncoder):

    def default(self, d):
        if isinstance(d, Dice):
            return {"class": 'dice', "name": d.name, "group": d.group, "image_path": str(d.image_path), "use": d.use}
        else:
            return super().default(d)
