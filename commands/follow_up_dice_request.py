import json


class FollowUpDiceRequest:
    def __init__(self, name, group, image_path, length, port):
        self.name = name
        self.group = group
        self.image_path = image_path
        self.length = length
        self.port = port


def decode_follow_up_dice_request(dct):
    if dct['class'] == "follow_up_dice_request":
        return FollowUpDiceRequest(dct['name'], dct['group'], dct['image_path'], dct['length'], dct['port'])
    return dct


class FollowUpDiceRequestEncoder(json.JSONEncoder):

    def default(self, d):
        if isinstance(d, FollowUpDiceRequest):
            return {"class": 'follow_up_dice_request', "name": d.name, "group": d.group, "image_path": d.image_path, "length": d.length, "port": d.port}
        else:
            return super().default(d)
