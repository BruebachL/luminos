import json


class OverlayMapInfo:

    def __init__(self, name, file_hash, revealed):
        self.name = name
        self.file_hash = file_hash
        self.revealed = revealed


def decode_map_overlay(dct):
    if dct['class'] == "overlay_map_info":
        return OverlayMapInfo(dct['name'], dct['file_hash'], dct['revealed'])
    return dct


class OverlayMapEncoder(json.JSONEncoder):

    def default(self, m):
        if isinstance(m, OverlayMapInfo):
            return {"class": 'overlay_map_info', "name": m.name, "file_hash": m.file_hash, "revealed": m.revealed}
        else:
            return super().default(m)
