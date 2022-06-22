import json


class InfoDiceRequest:
    def __init__(self, name, group, image_path, length, port):
        self.name = name
        self.group = group
        self.image_path = image_path
        self.length = length
        self.port = port


def decode_info_dice_request(dct):
    if dct['class'] == "info_dice_request":
        return InfoDiceRequest(dct['name'], dct['group'], dct['image_path'], dct['length'], dct['port'])
    return dct


class InfoDiceRequestEncoder(json.JSONEncoder):

    def default(self, d):
        if isinstance(d, InfoDiceRequest):
            return {"class": 'info_dice_request', "name": d.name, "group": d.group, "image_path": d.image_path, "length": d.length, "port": d.port}
        else:
            return super().default(d)
