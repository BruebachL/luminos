from PyQt5.QtWidgets import QWidget, QHBoxLayout, QCheckBox, QVBoxLayout

from clues.clue_image_widget import ClueImageWidget
from commands.command import CommandRevealClue


class ClueAdminDisplay(QWidget):

    def __init__(self, parent, clue_info):
        super().__init__(parent)
        self.setParent(parent)
        self.parent = parent
        self.clue_info = clue_info
        self.layout = QVBoxLayout()
        self.clue_image = ClueImageWidget(self.clue_info.file_path)
        self.revealed_checkbox = QCheckBox()
        self.revealed_checkbox.setChecked(self.clue_info.revealed)
        self.revealed_checkbox.stateChanged.connect(self.update_clue_revealed)
        self.revealed_checkbox.sizePolicy().setVerticalStretch(1)
        self.revealed_checkbox.sizePolicy().setHorizontalStretch(1)
        self.layout.addWidget(self.clue_image)
        self.layout.addWidget(self.revealed_checkbox)
        self.setLayout(self.layout)

    def update_clue_revealed(self):
        self.clue_info.revealed = self.revealed_checkbox.checkState()
        self.window().send_to_server(CommandRevealClue(self.clue_info.file_hash, self.clue_info.revealed))