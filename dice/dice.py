import hashlib
import json


class Dice:
    def __init__(self, display_name, group, image_path, use, checksum=None):
        self.display_name = display_name
        self.group = group
        if isinstance(image_path, str):
            self.image_path = image_path
        else:
            self.image_path = str(image_path)
        self.use = use
        if checksum is None:
            checksum = self.calculate_checksum()
        self.checksum = checksum

    def calculate_checksum(self):
        with open(self.image_path, "rb") as file:
            return hashlib.sha256(file.read()).hexdigest()


def decode_dice(dct):
    if dct['class'] == "dice":
        if 'checksum' in dct:
            checksum = dct['checksum']
        else:
            checksum = None
        return Dice(dct['display_name'], dct['group'], dct['image_path'], dct['use'], checksum)
    return dct


class DiceEncoder(json.JSONEncoder):

    def default(self, d):
        if isinstance(d, Dice):
            return {"class": 'dice', "display_name": d.display_name, "group": d.group, "image_path": str(d.image_path), "use": d.use, "checksum": d.checksum}
        else:
            return super().default(d)
