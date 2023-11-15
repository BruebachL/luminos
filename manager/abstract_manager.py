import hashlib
import json
import os
from os.path import isfile, join
from pathlib import Path

from PyQt5.QtWidgets import QWidget, QVBoxLayout


class AbstractManager(QWidget):

    def __init__(self, parent, basePath, manager_name, display_widget_class, managed_object_class, encoder, decoder):
        super().__init__(parent)
        self.parent = parent
        self.base_path = Path(basePath)
        self.manager_name = manager_name
        self.base_resource_path = Path.joinpath(self.base_path, Path("resources")).joinpath(Path(self.manager_name))
        if not os.path.exists(self.base_resource_path):
            os.mkdir(self.base_resource_path)
        self.config_file = Path.joinpath(self.base_path, self.manager_name + ".json")
        if not os.path.exists(self.config_file):
            try:
                open(self.config_file, 'x')
            except FileExistsError as e:
                pass

        self.file_hash_map = self.populate_file_hash_map()
        self.encoder = encoder
        self.decoder = decoder
        self.managed_objects = []
        self.managed_object_class = managed_object_class
        self.read_from_file()
        self.detect_unknown_objects()
        self.prune_deleted_objects()
        self.layout = QVBoxLayout()
        self.display_widget = None
        self.display_widget_class = display_widget_class
        self.update_layout()


    def update_layout(self):
        QWidget().setLayout(self.layout)
        self.layout = QVBoxLayout()
        self.display_widget = self.display_widget_class(self, self.managed_objects)
        self.layout.addWidget(self.display_widget)
        self.setLayout(self.layout)
        self.repaint()

    def get_managed_object_for_hash(self, file_hash):
        for managed_object in self.managed_objects:
            if managed_object.file_hash == file_hash:
                return managed_object
        return None

    def get_path_for_hash(self, file_hash):
        if file_hash in self.file_hash_map.keys():
            return self.file_hash_map[file_hash]
        return None

    def populate_file_hash_map(self):
        file_hash_map = {}
        onlyfiles = [join(self.base_resource_path, f) for f in os.listdir(self.base_resource_path) if isfile(join(self.base_resource_path, f))]
        for file_path in onlyfiles:
            with open(file_path, 'rb') as file:
                file_hash_map[hashlib.sha256(file.read()).hexdigest()] = str(file_path)
        return file_hash_map

    def gather_additional_object_info(self):
        print("Couldn't gather additional information about managed object of type: ", self.managed_object_class, " Not implemented!")
        return {}

    def detect_unknown_objects(self):
        for file_hash in self.file_hash_map.keys():
            if file_hash not in (managed_object.file_hash for managed_object in self.managed_objects):
                additional_info = self.gather_additional_object_info()
                self.managed_objects.append(self.managed_object_class(file_hash, self.file_hash_map[file_hash], **additional_info))

    def prune_deleted_objects(self):
        for managed_object in self.managed_objects:
            if managed_object.file_hash not in self.file_hash_map.keys():
                self.managed_objects.remove(managed_object)

    def read_from_file(self):
        file = open(self.config_file, "r")
        lines = file.readlines()
        for line in lines:
            self.managed_objects.append(json.loads(line, object_hook=self.decoder))

    def save_to_file(self):
        file = open(self.config_file, "w")
        for managed_object in self.managed_objects:
            if managed_object is not None:
                file.write(json.dumps(managed_object, cls=self.encoder) + "\n")
        file.close()
