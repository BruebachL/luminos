import json

from map.base_map_info import BaseMapInfo
from map.overlay_map_info import OverlayMapInfo, OverlayMapEncoder, decode_map_overlay
from utils.string_utils import fix_up_json_string


class MapInfo:

    def __init__(self, name, file_hash):
        self.name = name
        self.file_hash = file_hash


def decode_map(dct):
    if dct['class'] == "map_info":
        return MapInfo(dct['name'], dct['file_hash'])
    elif dct['class'] == "base_map_info":
        overlays = []
        for overlay in dct['overlays']:
            overlays.append(
                json.loads(str(overlay).replace('%', '"').replace("'", '"'), object_hook=decode_map_overlay))
        return BaseMapInfo(dct['name'], dct['file_hash'], overlays)
    elif dct['class'] == "overlay_map_info":
        return OverlayMapInfo(dct['name'], dct['file_hash'], dct['revealed'])
    return dct


class MapEncoder(json.JSONEncoder):

    def default(self, m):
        if isinstance(m, MapInfo):
            return {"class": 'map_info', "name": m.name, "file_hash": m.file_hash}
        elif isinstance(m, BaseMapInfo):
            json_overlays = []
            for overlay in m.overlays:
                json_overlays.append(fix_up_json_string(json.dumps(overlay, cls=OverlayMapEncoder, ensure_ascii=False)))
            return {"class": 'base_map_info', "name": m.name, "file_hash": m.file_hash, "overlays": json_overlays}
        elif isinstance(m, OverlayMapInfo):
            return {"class": 'overlay_map_info', "name": m.name, "file_hash": m.file_hash, "revealed": m.revealed}
        else:
            return super().default(m)
