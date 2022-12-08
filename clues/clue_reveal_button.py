import os

from PyQt5.QtWidgets import QPushButton


class ClueRevealButton(QPushButton):

    def __init__(self, parent, clue_info):
        super().__init__()
        self.parent = parent
        self.clue_info = clue_info

        self.setText(' '.join(os.path.split(clue_info.file_path)[1].split('clue_')[1:]))
        self.pressed.connect(self.toggle_overlay)

    def toggle_overlay(self):
        self.parent.toggle_clue_reveal(self.clue_info.file_hash)