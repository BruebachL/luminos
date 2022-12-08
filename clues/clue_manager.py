import hashlib
import json
import os
from math import ceil, sqrt
from os import listdir
from os.path import isfile, join
from pathlib import Path

from PyQt5.QtWidgets import QWidget, QGridLayout, QPushButton, QComboBox

from character.image_widget import ImageWidget
from clues.clue import Clue, ClueEncoder, decode_clue
from clues.clue_reveal_button import ClueRevealButton
from commands.command import CommandRevealClue, CommandEncoder


class ClueManager(QWidget):

    def __init__(self, parent, basePath):
        super().__init__(parent)
        self.parent = parent
        self.base_path = Path(basePath)
        self.base_resource_path = Path.joinpath(self.base_path, Path("resources")).joinpath(Path("clues"))
        if not os.path.exists(self.base_resource_path):
            os.mkdir(self.base_resource_path)
        self.clue_config_file = Path.joinpath(self.base_path, "clues.json")
        if not os.path.exists(self.clue_config_file):
            try:
                open(self.clue_config_file, 'x')
            except FileExistsError as e:
                pass
        self.file_hash_map = self.populate_file_hash_map()
        self.clues = []
        self.read_from_file()
        self.detect_unknown_clues()
        self.layout = QGridLayout()
        self.add_revealed_clues()
        self.add_admin_panel()
        self.setLayout(self.layout)

    def add_admin_panel(self):
        if self.parent is not None:
            if self.parent.admin_client:
                for clue in self.clues:
                    button = ClueRevealButton(self, clue)
                    self.layout.addWidget(button)

    def toggle_clue_reveal(self, file_hash):
        for clue in self.clues:
            if clue.file_hash == file_hash:
                if clue.revealed:
                    clue.revealed = False
                else:
                    clue.revealed = True
                self.parent.output_buffer.append(bytes(
                    json.dumps(CommandRevealClue(clue.file_hash, clue.revealed),
                               cls=CommandEncoder), "UTF-8"))
        self.update_layout()

    def update_layout(self):
        QWidget().setLayout(self.layout)
        self.layout = QGridLayout()
        self.add_revealed_clues()
        self.add_admin_panel()
        self.setLayout(self.layout)
        self.repaint()

    def add_revealed_clues(self):
        revealed_clues = self.get_revealed_clues()
        max_columns_per_row = ceil(sqrt(len(revealed_clues)))
        current_row = 0
        current_column = 0
        for clue in revealed_clues:
            self.layout.addWidget(ImageWidget(clue.file_path), current_row, current_column)
            current_column = current_column + 1
            if current_column == max_columns_per_row:
                current_column = 0
                current_row = current_row + 1

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
