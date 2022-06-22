import json


class InfoDiceRequestDecline:
    def __init__(self, name):
        self.name = name


def decode_info_dice_request_decline(dct):
    if dct['class'] == "info_dice_request_decline":
        return InfoDiceRequestDecline(dct['name'])
    return dct


class InfoDiceRequestDeclineEncoder(json.JSONEncoder):

    def default(self, d):
        if isinstance(d, InfoDiceRequestDecline):
            return {"class": 'info_dice_request_decline', "name": d.name}
        else:
            return super().default(d)
