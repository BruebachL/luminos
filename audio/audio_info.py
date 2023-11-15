import json

from manager.abstract_managed_object import AbstractManagedObject


class AudioInfo(AbstractManagedObject):

    def __init__(self, file_hash, file_path, **kwargs):
        super().__init__(file_hash, file_path, **kwargs)
        self.file_hash = file_hash
        self.file_path = file_path
        self.display_name = self.kwargs['display_name']


def decode_audio_info(dct):
    if dct['class'] == "audio_info":
        return AudioInfo(dct['file_hash'], dct['file_path'], **{"display_name": dct['display_name']})
    return dct


class AudioInfoEncoder(json.JSONEncoder):

    def default(self, a):
        if isinstance(a, AudioInfo):
            return {"class": 'audio_info', "file_hash": a.file_hash, "file_path": a.file_path, "display_name": a.display_name}
        else:
            return super().default(a)