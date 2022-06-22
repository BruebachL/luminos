import json


class CommandListenUp:
    def __init__(self, port):
        self.port = port


def decode_listen_up(dct):
    if dct['class'] == "listen_up":
        return CommandListenUp(dct['port'])
    return dct


class CommandListenUpEncoder(json.JSONEncoder):

    def default(self, l):
        if isinstance(l, CommandListenUp):
            return {"class": 'listen_up', "port": l.port}
        else:
            return super().default(l)
