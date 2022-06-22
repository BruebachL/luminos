import json


class CommandDiceRequest:
    def __init__(self, name, port):
        self.name = name
        self.port = port


def decode_command_dice_request(dct):
    if dct['class'] == "command_dice_request":
        return CommandDiceRequest(dct['name'], dct['port'])
    return dct


class CommandDiceRequestEncoder(json.JSONEncoder):

    def default(self, d):
        if isinstance(d, CommandDiceRequest):
            return {"class": 'command_dice_request', "name": d.name, "port": d.port}
        else:
            return super().default(d)
