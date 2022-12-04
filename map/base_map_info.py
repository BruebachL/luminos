import json


class BaseMapInfo:

    def __init__(self, name, file_hash, overlays):
        self.name = name
        self.file_hash = file_hash
        self.overlays = overlays


def decode_base_map(dct):
    if dct['class'] == "base_map_info":
        return BaseMapInfo(dct['name'], dct['file_hash'], dct['overlays'])
    return dct


class BaseMapEncoder(json.JSONEncoder):

    def default(self, m):
        if isinstance(m, BaseMapInfo):
            return {"class": 'base_map_info', "name": m.name, "file_hash": m.file_hash, "overlays": m.overlays}
        else:
            return super().default(m)
