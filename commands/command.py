import json

from commands.client_info import decode_client_info, ClientInfoEncoder
from utils.string_utils import fix_up_json_string

class CommandSendToClient:
    def __init__(self, client, command_to_send):
        self.client = client
        self.command_to_send = command_to_send

class CommandUpdateClient:
    def __init__(self, version, file_hashes):
        self.version = version
        self.file_hashes = file_hashes

class CommandUpdateClientInfo:
    def __init__(self, client_info):
        self.client_info = client_info

    def __str__(self):
        return json.dumps(self, cls=CommandEncoder)


class CommandQueryConnectedClients:
    def __init__(self, connected_client_infos):
        self.connected_client_infos = connected_client_infos


class CommandFileRequest:
    def __init__(self, file_hash, file_type, port):
        self.file_hash = file_hash
        self.file_type = file_type
        self.port = port


class CommandListenUp:
    def __init__(self, port, length, file_name):
        self.port = port
        self.length = length
        self.file_name = file_name


class CommandRevealClue:
    def __init__(self, file_hash, revealed):
        self.file_hash = file_hash
        self.revealed = revealed


class CommandRevealMapOverlay:
    def __init__(self, file_hash, revealed):
        self.file_hash = file_hash
        self.revealed = revealed


class CommandPlayAudio:
    def __init__(self, file_hash, duration):
        self.file_hash = file_hash
        self.duration = duration

class CommandPlayVideo:
    def __init__(self, file_hash, duration):
        self.file_hash = file_hash
        self.duration = duration

class CommandPlayStinger:
    def __init__(self, clue_hash, audio_hash, duration):
        self.clue_hash = clue_hash
        self.audio_hash = audio_hash
        self.duration = duration

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


class InfoFileRequest:
    def __init__(self, name, extension, file_type, file_length, file_hash, file_info):
        self.name = name
        self.extension = extension
        self.file_type = file_type
        self.file_length = file_length
        self.file_hash = file_hash
        self.file_info = file_info


class InfoUpdateFile(object):
    def __init__(self, relative_path):
        super().__init__()
        self.relative_path = relative_path


class InfoAudioFile:
    def __init__(self, display_name):
        self.display_name = display_name

class InfoVideoFile:
    def __init__(self, display_name):
        self.display_name = display_name

class InfoDiceFile:
    def __init__(self, display_name, group):
        self.display_name = display_name
        self.group = group

class InfoClueFile:
    def __init__(self, display_name, revealed):
        self.display_name = display_name
        self.revealed = revealed

class InfoMapFile:
    def __init__(self, base_map, revealed):
        self.base_map = base_map
        self.revealed = revealed

def decode_command(dct):
    if 'class' in dct:
        match(dct['class']):
            case "command_send_to_client":
                return CommandSendToClient(dct['client'], dct['command_to_send'])
            case "command_update_client":
                return CommandUpdateClient(dct['version'], dct['file_hashes'])
            case "command_update_client_info":
                return CommandUpdateClientInfo(json.loads(str(dct['client_info']).replace("'", '"'), object_hook=decode_client_info))
            case "command_query_connected_clients":
                client_infos = []
                for connected_client_info in dct['client_infos']:
                    client_infos.append(json.loads(str(connected_client_info).replace("'", '"').replace('True', 'true').replace('False', 'false').replace('None', 'null'), object_hook=decode_client_info))
                return CommandQueryConnectedClients(client_infos)
            case "command_file_request":
                return CommandFileRequest(dct['file_hash'], dct['file_type'], dct['port'])
            case "listen_up":
                return CommandListenUp(dct['port'], dct['length'], dct['filename'])
            case "command_roll_dice":
                return CommandRollDice(dct['character'], dct['amount'], dct['sides'], dct['rolled_for'], dct['rolled_against'], dct['equalizer'], dct['dice_skins'])
            case "info_roll_dice":
                return InfoRollDice(dct['player'], dct['roll_value'], dct['dice_used'], dct['rolled_for'], dct['rolled_against'], dct['success'], dct['dice_skins'])
            case "info_dice_request_decline":
                return InfoDiceRequestDecline(dct['name'])
            case "info_file_request":
                return InfoFileRequest(dct['name'], dct['extension'], dct['file_type'], dct['file_length'], dct['file_hash'], dct['file_info'])
            case "info_update_file":
                return InfoUpdateFile(dct['relative_path'])
            case "info_audio_file":
                return InfoAudioFile(dct['display_name'])
            case "info_video_file":
                return InfoVideoFile(dct['display_name'])
            case "info_dice_file":
                return InfoDiceFile(dct['display_name'], dct['group'])
            case "info_clue_file":
                return InfoClueFile(dct['display_name'], dct['revealed'])
            case "info_map_file":
                return InfoMapFile(dct['base_map'], dct['revealed'])
            case "command_reveal_clue":
                return CommandRevealClue(dct['file_hash'], dct['revealed'])
            case "command_reveal_map_overlay":
                return CommandRevealMapOverlay(dct['file_hash'], dct['revealed'])
            case "command_play_audio":
                return CommandPlayAudio(dct['file_hash'], dct['duration'])
            case "command_play_video":
                return CommandPlayVideo(dct['file_hash'], dct['duration'])
            case "command_play_stinger":
                return CommandPlayStinger(dct['clue_hash'], dct['audio_hash'], dct['duration'])
    return dct


class CommandEncoder(json.JSONEncoder):

    def default(self, c):
        if isinstance(c, CommandSendToClient):
            return {"class": "command_send_to_client", "client": c.client, "command_to_send": c.command_to_send}
        if isinstance(c, CommandUpdateClient):
            return {"class": "command_update_client", "version": c.version, "file_hashes": c.file_hashes}
        if isinstance(c, CommandUpdateClientInfo):
            return {"class": "command_update_client_info", "client_info": fix_up_json_string(json.dumps(c.client_info, cls=ClientInfoEncoder))}
        if isinstance(c, CommandQueryConnectedClients):
            json_infos = []
            for client_info in c.connected_client_infos:
                json_infos.append(fix_up_json_string(json.dumps(client_info, cls=ClientInfoEncoder)))
            return {"class": "command_query_connected_clients", "client_infos": json_infos}
        if isinstance(c, CommandFileRequest):
            return {"class": 'command_file_request', "file_hash": c.file_hash, "file_type": c.file_type,"port": c.port}
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
        elif isinstance(c, InfoFileRequest):
            return {"class": 'info_file_request', "name": c.name, "extension": c.extension, "file_type": c.file_type,
                    "file_length": c.file_length, "file_hash": c.file_hash, "file_info": fix_up_json_string(json.dumps(c.file_info, cls=CommandEncoder))}
        elif isinstance(c, InfoUpdateFile):
            return {"class": 'info_update_file', "relative_path": c.relative_path}
        elif isinstance(c, InfoAudioFile):
            return {"class": 'info_audio_file', "display_name": c.display_name}
        elif isinstance(c, InfoVideoFile):
            return {"class": 'info_video_file', "display_name": c.display_name}
        elif isinstance(c, InfoDiceFile):
            return {"class": 'info_dice_file', "display_name": c.display_name, "group": c.group}
        elif isinstance(c, InfoClueFile):
            return {"class": 'info_clue_file', "display_name": c.display_name, "revealed": c.revealed}
        elif isinstance(c, InfoMapFile):
            return {"class": 'info_map_file', "base_map": c.base_map, "revealed": c.revealed}
        elif isinstance(c, CommandRevealClue):
            return {"class": 'command_reveal_clue', "file_hash": c.file_hash, "revealed": c.revealed}
        elif isinstance(c, CommandRevealMapOverlay):
            return {"class": 'command_reveal_map_overlay', "file_hash": c.file_hash, "revealed": c.revealed}
        elif isinstance(c, CommandPlayAudio):
            return {"class": 'command_play_audio', "file_hash": c.file_hash, "duration": c.duration}
        elif isinstance(c, CommandPlayVideo):
            return {"class": 'command_play_video', "file_hash": c.file_hash, "duration": c.duration}
        elif isinstance(c, CommandPlayStinger):
            return {"class": 'command_play_stinger', 'clue_hash': c.clue_hash, 'audio_hash': c.audio_hash, 'duration': c.duration}
        else:
            return super().default(c)
