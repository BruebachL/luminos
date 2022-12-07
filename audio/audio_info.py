import json


class AudioInfo(object):

    def __init__(self, file_hash, file_path, display_name):
        self.file_hash = file_hash
        self.file_path = file_path
        self.display_name = display_name


def decode_audio_info(dct):
    if dct['class'] == "audio_info":
        return AudioInfo(dct['file_hash'], dct['file_path'], dct['display_name'])
    return dct


class AudioInfoEncoder(json.JSONEncoder):

    def default(self, a):
        if isinstance(a, AudioInfo):
            return {"class": 'audio_info', "file_hash": a.file_hash, "file_path": a.file_path, "display_name": a.display_name}
        else:
            return super().default(a)