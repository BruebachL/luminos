import json

from map.overlay_map_info import OverlayMapEncoder, decode_map_overlay
from utils.string_utils import fix_up_json_string


class BaseMapInfo:

    def __init__(self, name, file_hash, overlays):
        self.name = name
        self.file_hash = file_hash
        self.overlays = overlays


def decode_base_map(dct):
    if dct['class'] == "base_map_info":
        overlays = []
        for overlay in dct['overlays']:
            overlays.append(
                json.loads(str(overlay).replace('%', '"').replace("'", '"'), object_hook=decode_map_overlay))
        return BaseMapInfo(dct['name'], dct['file_hash'], overlays)
    return dct


class BaseMapEncoder(json.JSONEncoder):

    def default(self, m):
        if isinstance(m, BaseMapInfo):
            json_overlays = []
            for overlay in m.overlays:
                json_overlays.append(fix_up_json_string(json.dumps(overlay, cls=OverlayMapEncoder, ensure_ascii=False)))
            return {"class": 'base_map_info', "name": m.name, "file_hash": m.file_hash, "overlays": json_overlays}
        else:
            return super().default(m)
