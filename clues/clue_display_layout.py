from math import sqrt, ceil

from PyQt5.QtWidgets import QGridLayout, QWidget

from character.image_widget import ImageWidget


class ClueDisplayLayout(QWidget):

    def __init__(self, clue_manager):
        super().__init__()
        self.clue_manager = clue_manager
        self.grid_layout = QGridLayout()
        self.add_revealed_clues()
        self.setLayout(self.grid_layout)

    def add_revealed_clues(self):
        revealed_clues = self.clue_manager.get_revealed_clues()
        max_columns_per_row = ceil(sqrt(len(revealed_clues)))
        current_row = 0
        current_column = 0
        for clue in revealed_clues:
            self.grid_layout.addWidget(ImageWidget(clue.file_path), current_row, current_column)
            current_column = current_column + 1
            if current_column == max_columns_per_row:
                current_column = 0
                current_row = current_row + 1