import hashlib
import json
import os
from os import listdir
from os.path import isfile, join
from pathlib import Path

from PyQt5.QtWidgets import QWidget, QGridLayout, QTabWidget, QVBoxLayout

from notes.note import Note, decode_note, NoteEncoder
from notes.note_widget import NoteWidget
from notes.notes_tab_widget import NotesTabWidget


class NoteManager(QWidget):

    def __init__(self, parent, basePath):
        super().__init__(parent)
        self.parent = parent
        self.base_path = Path(basePath)
        self.base_resource_path = Path.joinpath(self.base_path, Path("resources")).joinpath(Path("notes"))
        if not os.path.exists(self.base_resource_path):
            os.mkdir(self.base_resource_path)
        self.note_config_file = Path.joinpath(self.base_path, "notes.json")
        if not os.path.exists(self.note_config_file):
            try:
                open(self.note_config_file, 'x')
            except FileExistsError as e:
                pass

        self.file_hash_map = self.populate_file_hash_map()
        self.notes = []
        self.read_from_file()
        self.detect_unknown_notes()
        self.layout = QVBoxLayout()
        self.note_tabs = None
        self.update_layout()


    def update_layout(self):
        QWidget().setLayout(self.layout)
        self.layout = QVBoxLayout()
        self.note_tabs = NotesTabWidget(self, self.notes)
        self.layout.addWidget(self.note_tabs)
        self.setLayout(self.layout)
        self.repaint()

    def get_note_for_hash(self, file_hash):
        for note in self.notes:
            if note.file_hash == file_hash:
                return note
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

    def detect_unknown_notes(self):
        for file_hash in self.file_hash_map.keys():
            if file_hash not in (note.file_hash for note in self.notes):
                with open(self.file_hash_map[file_hash]) as file:
                    content = file.read()
                    self.notes.append(Note(file_hash, self.file_hash_map[file_hash], ''.join(os.path.split(self.file_hash_map[file_hash])[1].split('.txt')[:-1]), content))

    def read_from_file(self):
        file = open(self.note_config_file, "r")
        lines = file.readlines()
        for line in lines:
            self.notes.append(json.loads(line, object_hook=decode_note))

    def save_to_file(self):
        file = open(self.note_config_file, "w")
        for note in self.notes:
            if note is not None:
                file.write(json.dumps(note, cls=NoteEncoder) + "\n")
                with open(note.file_path, "w") as actual_file:
                    actual_file.write(note.content)
        file.close()
