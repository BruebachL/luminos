import json


class MapInfo:

    def __init__(self, name, file_hash):
        self.name = name
        self.file_hash = file_hash


def decode_map(dct):
    if dct['class'] == "map_info":
        return MapInfo(dct['name'], dct['file_hash'])
    return dct


class MapEncoder(json.JSONEncoder):

    def default(self, m):
        if isinstance(m, MapInfo):
            return {"class": 'map_info', "name": m.name, "file_hash": m.file_hash}
        else:
            return super().default(m)
