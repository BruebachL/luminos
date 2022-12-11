import json

from character.character import decode_character, CharacterEncoder, Character
from utils.string_utils import fix_up_json_string


class ClientInfo(object):

    def __init__(self, client_id, client_friendly_name, version, status, character):
        self.client_id = client_id
        self.client_friendly_name = client_friendly_name
        self.version = version
        self.status = status
        self.character = character


def decode_client_info(dct):
    if dct['class'] == "client_info":
        character = json.loads(str(dct['character']).replace("'", '"'), object_hook=decode_character) if dct['character'] != 'null' and \
                                                                                                         dct['character'] is not None and dct['character'] != 'None' else None
        return ClientInfo(dct['client_id'], dct['client_friendly_name'], dct['version'], dct['status'], character)
    return dct


class ClientInfoEncoder(json.JSONEncoder):

    def default(self, c):
        print(c)
        if isinstance(c, ClientInfo):
            json_character = fix_up_json_string(json.dumps(c.character, cls=CharacterEncoder))
            return {"class": 'client_info', "client_id": c.client_id, "client_friendly_name": c.client_friendly_name, "version": c.version,
                    "status": c.status, "character": json_character}
        else:
            return super().default(c)