import json


class VideoInfo(object):

    def __init__(self, file_hash, file_path, display_name):
        self.file_hash = file_hash
        self.file_path = file_path
        self.display_name = display_name


def decode_video_info(dct):
    if dct['class'] == "video_info":
        return VideoInfo(dct['file_hash'], dct['file_path'], dct['display_name'])
    return dct


class VideoInfoEncoder(json.JSONEncoder):

    def default(self, a):
        if isinstance(a, VideoInfo):
            return {"class": 'video_info', "file_hash": a.file_hash, "file_path": a.file_path, "display_name": a.display_name}
        else:
            return super().default(a)