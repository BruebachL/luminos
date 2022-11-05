import json


class CommandDiceRequest:
    def __init__(self, name, port):
        self.name = name
        self.port = port


class CommandListenUp:
    def __init__(self, port, length, file_name):
        self.port = port
        self.length = length
        self.file_name = file_name

class CommandRollDice:

    def __init__(self, character, amount, sides, rolled_for, rolled_against, equalizer, dice_skins):
        self.character = character
        self.amount = amount
        self.sides = sides
        self.rolled_for = rolled_for
        self.rolled_against = rolled_against
        self.equalizer = equalizer
        self.dice_skins = dice_skins


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


class InfoDiceRequestDecline:
    def __init__(self, name):
        self.name = name


class InfoDiceRequest:
    def __init__(self, name, group, image_path, length, port):
        self.name = name
        self.group = group
        self.image_path = image_path
        self.length = length
        self.port = port

class FollowUpDiceRequest:
    def __init__(self, name, group, image_path, length, port):
        self.name = name
        self.group = group
        self.image_path = image_path
        self.length = length
        self.port = port


def decode_command(dct):
    match(dct['class']):
        case "command_dice_request":
            return CommandDiceRequest(dct['name'], dct['port'])
        case "listen_up":
            return CommandListenUp(dct['port'], dct['length'], dct['filename'])
        case "command_roll_dice":
            return CommandRollDice(dct['character'], dct['amount'], dct['sides'], dct['rolled_for'], dct['rolled_against'], dct['equalizer'], dct['dice_skins'])
        case "info_roll_dice":
            return InfoRollDice(dct['player'], dct['roll_value'], dct['dice_used'], dct['rolled_for'], dct['rolled_against'], dct['success'], dct['dice_skins'])
        case "info_dice_request_decline":
            return InfoDiceRequestDecline(dct['name'])
        case "info_dice_request":
            return InfoDiceRequest(dct['name'], dct['group'], dct['image_path'], dct['length'], dct['port'])
        case "follow_up_dice_request":
            return FollowUpDiceRequest(dct['name'], dct['group'], dct['image_path'], dct['length'], dct['port'])
    return dct


class CommandEncoder(json.JSONEncoder):

    def default(self, c):
        if isinstance(c, CommandDiceRequest):
            return {"class": 'command_dice_request', "name": c.name, "port": c.port}
        elif isinstance(c, CommandListenUp):
            return {"class": 'listen_up', "port": c.port, "length": c.length, "filename": c.file_name}
        elif isinstance(c, CommandRollDice):
            return {"class": 'command_roll_dice', "character": c.character, "amount": c.amount, "sides": c.sides,
                    "rolled_for": c.rolled_for, "rolled_against": c.rolled_against, "equalizer": c.equalizer,
                    "dice_skins": c.dice_skins}
        elif isinstance(c, InfoRollDice):
            return {"class": 'info_roll_dice', "player": c.player, "roll_value": c.roll_value, "dice_used": c.dice_used,
                    "rolled_for": c.rolled_for, "rolled_against": c.rolled_against, "success": c.success,
                    "dice_skins": c.dice_skins}
        elif isinstance(c, InfoDiceRequestDecline):
            return {"class": 'info_dice_request_decline', "name": c.name}
        elif isinstance(c, InfoDiceRequest):
            return {"class": 'info_dice_request', "name": c.name, "group": c.group, "image_path": c.image_path,
                    "length": c.length, "port": c.port}
        elif isinstance(c, FollowUpDiceRequest):
            return {"class": 'follow_up_dice_request', "name": c.name, "group": c.group, "image_path": c.image_path,
                    "length": c.length, "port": c.port}
        else:
            return super().default(c)
