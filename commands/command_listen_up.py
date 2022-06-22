import json


class CommandListenUp:
    def __init__(self, port, length, file_name):
        self.port = port
        self.length = length
        self.file_name = file_name


def decode_listen_up(dct):
    if dct['class'] == "listen_up":
        return CommandListenUp(dct['port'], dct['length'], dct['filename'])
    return dct


class CommandListenUpEncoder(json.JSONEncoder):

    def default(self, l):
        if isinstance(l, CommandListenUp):
            return {"class": 'listen_up', "port": l.port, "length": l.length, "filename": l.file_name}
        else:
            return super().default(l)
