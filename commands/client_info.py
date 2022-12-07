import json


class ClientInfo(object):

    def __init__(self, client_id, client_friendly_name, version, status):
        self.client_id = client_id
        self.client_friendly_name = client_friendly_name
        self.version = version
        self.status = status

    def __str__(self):
        return json.dumps(self, cls=ClientInfoEncoder)


def decode_client_info(dct):
    if dct['class'] == "client_info":
        return ClientInfo(dct['client_id'], dct['client_friendly_name'], dct['version'], dct['status'])
    return dct


class ClientInfoEncoder(json.JSONEncoder):

    def default(self, c):
        if isinstance(c, ClientInfo):
            return {"class": 'client_info', "client_id": c.client_id, "client_friendly_name": c.client_friendly_name, "version": c.version,
                    "status": c.status}
        else:
            return super().default(c)