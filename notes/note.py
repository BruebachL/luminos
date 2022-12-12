import json


class Note(object):

    def __init__(self, file_hash, file_path, display_name, content):
        self.file_hash = file_hash
        self.file_path = file_path
        self.display_name = display_name
        self.content = content


def decode_note(dct):
    if dct['class'] == "note":
        return Note(dct['file_hash'], dct['file_path'], dct['display_name'], dct['content'])
    return dct


class NoteEncoder(json.JSONEncoder):

    def default(self, c):
        if isinstance(c, Note):
            return {"class": 'note', "file_hash": c.file_hash, "file_path": c.file_path, "display_name": c.display_name,
                    "content": c.content}
        else:
            return super().default(c)