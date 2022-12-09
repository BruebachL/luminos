from PyQt5.QtWidgets import QWidget, QHBoxLayout, QCheckBox

from character.image_widget import ImageWidget
from commands.command import CommandRevealClue


class ClueAdminDisplay(QWidget):

    def __init__(self, parent, clue_info):
        super().__init__(parent)
        self.setParent(parent)
        self.parent = parent
        self.clue_info = clue_info
        self.layout = QHBoxLayout()
        self.clue_image = ImageWidget(self.clue_info.file_path)
        self.revealed_checkbox = QCheckBox()
        self.revealed_checkbox.setChecked(self.clue_info.revealed)
        self.revealed_checkbox.stateChanged.connect(self.update_clue_revealed)
        self.layout.addWidget(self.clue_image)
        self.layout.addWidget(self.revealed_checkbox)
        self.setLayout(self.layout)

    def update_clue_revealed(self):
        self.clue_info.revealed = self.revealed_checkbox.checkState()
        self.window().send_to_server(CommandRevealClue(self.clue_info.file_hash, self.clue_info.revealed))