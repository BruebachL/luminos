from PyQt5.QtWidgets import QWidget, QVBoxLayout

from dice.dice_roll_viewer_row import DiceRollViewerRow


class DiceRollViewer(QWidget):

    def __init__(self, dice_manager):
        super().__init__()
        self.dice_rolls = []
        self.buffer_size = 5
        self.dice_manager = dice_manager
        self.layout = QVBoxLayout()
        for dice_roll in self.dice_rolls:
            self.layout.addWidget(DiceRollViewerRow(dice_roll, self.dice_manager))
        self.setLayout(self.layout)

    def add_dice_roll(self, dice_roll, dice_skins):
        if len(self.dice_rolls) >= self.buffer_size:
            self.layout.removeWidget(self.layout.itemAt(0).widget())
            self.dice_rolls.pop(0)
        self.dice_rolls.append(dice_roll)
        self.layout.addWidget(DiceRollViewerRow(dice_roll, dice_skins, self.dice_manager))
