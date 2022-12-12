import os

from PyQt5.QtWidgets import QTabWidget, QWidget, QInputDialog, QLineEdit

from notes.note import Note
from notes.note_widget import NoteWidget


class NotesTabWidget(QTabWidget):
    def __init__(self, parent, notes):
        super().__init__(parent)
        print("Note tab manager created with ", notes)
        self.parent = parent
        self.notes = notes
        self.input_dialog = QInputDialog()
        self.add_note_tab = QWidget()
        self.currentChanged.connect(self.check_if_create_new_note_tab_was_selected)
        self.add_note_tabs()



    def add_note_tabs(self):
        for note in self.notes:
            self.addTab(NoteWidget(self, note), note.display_name)
        self.addTab(self.add_note_tab, "+")

    def check_if_create_new_note_tab_was_selected(self):
        if self.currentWidget() == self.add_note_tab:
            if self.notes:
                new_talent_group_name = self.input_dialog.getText(self, "Add new note", "Please enter a name for the new note:", QLineEdit.Normal)
                new_path = os.path.join(self.parent.base_resource_path, new_talent_group_name[0] + ".txt")
                if new_talent_group_name[1]:
                    if not os.path.exists(new_path):
                        try:
                            with open(new_path, 'x') as file:
                                file.write(new_talent_group_name[0])
                        except FileExistsError as e:
                            pass
                    self.parent.file_hash_map = self.parent.populate_file_hash_map()
                    self.parent.notes = []
                    self.parent.read_from_file()
                    self.parent.detect_unknown_notes()
                    self.prune_deleted_notes()
                    self.parent.update_layout()
            else:
                new_path = os.path.join(self.parent.base_resource_path, "default.txt")
                if not os.path.exists(new_path):
                    try:
                        with open(new_path, 'x') as file:
                            file.write("This is a default note.")
                    except FileExistsError as e:
                        pass
                self.parent.file_hash_map = self.parent.populate_file_hash_map()
                self.parent.notes = []
                self.parent.read_from_file()
                self.parent.detect_unknown_notes()
                self.prune_deleted_notes()
                self.notes = self.parent.notes
                for i in range(self.count()):
                    self.widget(i).setParent(QWidget())
                self.add_note_tab = QWidget()
                self.add_note_tabs()