import hashlib
import json
from os import listdir
from os.path import isfile, join
from pathlib import Path

from PyQt5.QtWidgets import QWidget, QVBoxLayout, QPushButton, QComboBox

from commands.command import CommandRevealMapOverlay, CommandEncoder
from map.base_map_info import BaseMapInfo, BaseMapEncoder, decode_base_map
from map.map_display_widget import MapDisplayWidget
from map.overlay_map_info import OverlayMapInfo, OverlayMapEncoder


class MapManager(QWidget):

    def __init__(self, parent, basePath):
        super().__init__(parent)
        self.parent = parent
        self.base_path = Path(basePath)
        self.base_resource_path = Path.joinpath(self.base_path, Path("resources")).joinpath(Path("maps"))
        self.map_config_file = Path.joinpath(self.base_path, "map.json")
        self.file_hash_map = self.populate_file_hash_map()
        self.base_maps = self.get_base_maps_from_file_paths()
        self.overlays = self.get_overlays_from_file_paths()
        self.map_infos = []
        self.base_map_infos = []
        self.overlay_map_infos = []
        self.active_map = 0
        self.read_from_file()
        self.detect_unknown_maps()
        self.sort_overlays_to_base_maps()
        # self.determine_active_map/setup_map()
        self.image_widget = MapDisplayWidget(self.get_active_map())
        self.layout = QVBoxLayout(self)
        self.layout.addWidget(self.image_widget)
        self.combo_box = None
        self.add_admin_panel()
        self.setLayout(self.layout)
        self.repaint()

    def add_admin_panel(self):
        if self.parent is not None:
            if self.parent.admin_client:
                button = QPushButton()
                button.pressed.connect(self.toggle_map_overlay)
                self.layout.addWidget(button)
                active_base_map = self.get_active_map()
                self.combo_box = QComboBox()
                for overlay in active_base_map.overlays:
                    self.combo_box.addItem(overlay.name)
                self.combo_box.setCurrentText(active_base_map.overlays[0].name)
                #combo_box.currentTextChanged.connect(self.update_combo)
                #combo_box.currentIndexChanged.connect(self.update_combo)
                #combo_box.editTextChanged.connect(self.update_combo)
                self.layout.addWidget(self.combo_box)

    def toggle_map_overlay(self):
        print(self.combo_box.currentText())
        for i in range(len(self.get_active_map().overlays)):
            if self.get_active_map().overlays[i].name == self.combo_box.currentText():
                if self.get_active_map().overlays[i].revealed:
                    self.get_active_map().overlays[i].revealed = False
                else:
                    self.get_active_map().overlays[i].revealed = True
                self.parent.output_buffer.append(bytes(
                    json.dumps(CommandRevealMapOverlay(self.get_active_map().overlays[i].file_hash,
                                                       self.get_active_map().overlays[i].revealed),
                               cls=CommandEncoder), "UTF-8"))
        self.update_layout()

    def update_layout(self):
        self.image_widget.parent = None
        self.image_widget = MapDisplayWidget(self.get_active_map())
        QWidget().setLayout(self.layout)
        self.layout = QVBoxLayout(self)
        self.layout.addWidget(self.image_widget)
        self.add_admin_panel()
        self.setLayout(self.layout)
        self.repaint()

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
        return self.base_map_infos[self.active_map]

    def get_paths_for_overlays(self):
        paths = []
        for file_hash in self.overlays:
            paths.append(self.file_hash_map[file_hash])
        return paths

    def get_path_for_hash(self, file_hash):
        if file_hash in self.file_hash_map.keys():
            return self.file_hash_map[file_hash]
        return None

    def get_map_info_for_hash(self, file_hash):
        for base_map_info in self.base_map_infos:
            if base_map_info.file_hash == file_hash:
                return base_map_info
            else:
                for overlay_info in base_map_info.overlays:
                    if overlay_info.file_hash == file_hash:
                        return overlay_info
        for overlay_info in self.overlay_map_infos:
            if overlay_info.file_hash == file_hash:
                return file_hash
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
            if file_hash not in (map_info.file_hash for map_info in self.base_map_infos) and file_hash not in (map_info.file_hash for map_info in self.overlay_map_infos):
                if self.is_base_map(file_hash):
                    self.base_map_infos.append(BaseMapInfo(self.file_hash_map[file_hash], file_hash, []))
                else:
                    self.overlay_map_infos.append(OverlayMapInfo(self.file_hash_map[file_hash], file_hash, False))

    def sort_overlays_to_base_maps(self):
        for base_map in self.base_map_infos:
            for overlay in self.overlay_map_infos:
                if base_map.name.split('base_map')[0] in overlay.name and overlay.name not in (overlay_info.name for overlay_info in base_map.overlays):
                    base_map.overlays.append(overlay)


    def reveal_map_overlay(self, file_hash):
        for base_map_info in self.base_map_infos:
            for overlay_info in base_map_info.overlays:
                if overlay_info.file_hash == file_hash:
                    overlay_info.revealed = True


    def read_from_file(self):
        file = open(self.map_config_file, "r")
        lines = file.readlines()
        for line in lines:
            self.base_map_infos.append(json.loads(line, object_hook=decode_base_map))

    def save_to_file(self):
        file = open(self.map_config_file, "w")
        for map_info in self.base_map_infos:
            if map_info is not None:
                file.write(json.dumps(map_info, cls=BaseMapEncoder) + "\n")
        file.close()

    def resizeEvent(self, event):
        super().resizeEvent(event)
