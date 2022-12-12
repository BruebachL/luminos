import os

from PyQt5.QtWidgets import QWidget, QVBoxLayout, QPushButton

from notes.note_widget import NoteWidget


class NoteControlWidget(QWidget):

    def __init__(self, parent, note):
        super().__init__(parent)
        self.parent = parent
        self.note = note
        self.layout = QVBoxLayout()
        self.note_widget = NoteWidget(self, self.note)
        self.delete_button = QPushButton("Delete note")
        self.delete_button.clicked.connect(self.delete_note)
        self.layout.addWidget(self.note_widget)
        self.layout.addWidget(self.delete_button)
        self.setLayout(self.layout)

    def delete_note(self):
        self.parent.parent.notes.remove(self.note)
        os.remove(self.note.file_path)
        self.parent.parent.file_hash_map = self.parent.parent.populate_file_hash_map()
        self.parent.parent.notes = []
        self.parent.parent.read_from_file()
        self.parent.parent.detect_unknown_notes()
        self.parent.parent.prune_deleted_notes()
        self.parent.parent.update_layout()