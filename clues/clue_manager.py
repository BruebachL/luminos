import hashlib
import json
from os import listdir
from os.path import isfile, join
from pathlib import Path

from clues.clue import Clue, ClueEncoder, decode_clue


class ClueManager(object):

    def __init__(self, basePath):
        super().__init__()
        self.base_path = Path(basePath)
        self.base_resource_path = Path.joinpath(self.base_path, Path("resources")).joinpath(Path("clues"))
        self.clue_config_file = Path.joinpath(self.base_path, "clues.json")
        self.file_hash_map = self.populate_file_hash_map()
        print(self.file_hash_map)
        self.clues = []
        self.read_from_file()
        self.detect_unknown_clues()

    def get_revealed_clues(self):
        revealed_clues = []
        for clue in self.clues:
            if clue.revealed:
                revealed_clues.append(clue)
        return revealed_clues

    def get_clue_for_hash(self, file_hash):
        for clue in self.clues:
            if clue.file_hash == file_hash:
                return clue
        return None

    def get_path_for_hash(self, file_hash):
        if file_hash in self.file_hash_map.keys():
            return self.file_hash_map[file_hash]
        return None

    def populate_file_hash_map(self):
        file_hash_map = {}
        onlyfiles = [join(self.base_resource_path, f) for f in listdir(self.base_resource_path) if isfile(join(self.base_resource_path, f))]
        for file_path in onlyfiles:
            with open(file_path, 'rb') as file:
                file_hash_map[hashlib.sha256(file.read()).hexdigest()] = str(file_path)
        return file_hash_map

    def detect_unknown_clues(self):
        for file_hash in self.file_hash_map.keys():
            if file_hash not in (clue.file_hash for clue in self.clues):
                self.clues.append(Clue(file_hash, self.file_hash_map[file_hash], "Unknown", True))

    def read_from_file(self):
        file = open(self.clue_config_file, "r")
        lines = file.readlines()
        for line in lines:
            self.clues.append(json.loads(line, object_hook=decode_clue))

    def save_to_file(self):
        file = open(self.clue_config_file, "w")
        for clue in self.clues:
            if clue is not None:
                file.write(json.dumps(clue, cls=ClueEncoder) + "\n")
        file.close()
