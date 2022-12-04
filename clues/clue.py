import json


class Clue(object):

    def __init__(self, file_hash, file_path, display_name, revealed):
        self.file_hash = file_hash
        self.file_path = file_path
        self.display_name = display_name
        self.revealed = revealed


def decode_clue(dct):
    if dct['class'] == "clue":
        return Clue(dct['file_hash'], dct['file_path'], dct['display_name'], dct['revealed'])
    return dct


class ClueEncoder(json.JSONEncoder):

    def default(self, c):
        if isinstance(c, Clue):
            return {"class": 'clue', "file_hash": c.file_hash, "file_path": c.file_path, "display_name": c.display_name,
                    "revealed": c.revealed}
        else:
            return super().default(c)