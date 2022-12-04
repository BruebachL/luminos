import hashlib
import json
from os import listdir
from os.path import isfile, join
from pathlib import Path

from map.map_info import decode_map, MapEncoder, MapInfo


class MapManager(object):

    def __init__(self, basePath):
        super().__init__()
        self.base_path = Path(basePath)
        self.base_resource_path = Path.joinpath(self.base_path, Path("resources")).joinpath(Path("maps"))
        self.map_config_file = Path.joinpath(self.base_path, "map.json")
        self.file_hash_map = self.populate_file_hash_map()
        self.base_maps = self.get_base_maps_from_file_paths()
        self.overlays = self.get_overlays_from_file_paths()
        self.map_infos = []
        self.active_map = 0
        self.read_from_file()
        self.detect_unknown_maps()
        # self.determine_active_map/setup_map()

    def is_base_map(self, file_hash):
        return "base_map" in self.file_hash_map[file_hash]

    def get_base_maps_from_file_paths(self):
        base_maps = []
        for file_hash in self.file_hash_map.keys():
            if self.is_base_map(file_hash):
                base_maps.append(file_hash)
        return base_maps

    def get_overlays_from_file_paths(self):
        overlays = []
        for file_hash in self.file_hash_map.keys():
            if not self.is_base_map(file_hash):
                overlays.append(file_hash)
        return overlays


    def get_active_map(self):
        return self.file_hash_map[self.map_infos[self.active_map].file_hash]

    def get_paths_for_overlays(self):
        paths = []
        for file_hash in self.overlays:
            paths.append(self.file_hash_map[file_hash])
        return paths

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

    def detect_unknown_maps(self):
        for file_hash in self.file_hash_map.keys():
            if file_hash not in (map_info.file_hash for map_info in self.map_infos):
                self.map_infos.append(MapInfo(self.file_hash_map[file_hash], file_hash))


    def read_from_file(self):
        file = open(self.map_config_file, "r")
        lines = file.readlines()
        for line in lines:
            self.map_infos.append(json.loads(line, object_hook=decode_map))

    def save_to_file(self):
        file = open(self.map_config_file, "w")
        for map_info in self.map_infos:
            if map_info is not None:
                file.write(json.dumps(map_info, cls=MapEncoder) + "\n")
        file.close()
