from PyQt5.QtWidgets import QListWidget, QVBoxLayout, QWidget
from dice.dice_roll_button_layout import DiceRollButtonLayout
from dice.dice_roll_viewer import DiceRollViewer


class DiceRollManagerLayout(QWidget):
    def __init__(self, output_buffer, player, dice_manager):
        super().__init__()
        self.dice_manager = dice_manager
        self.output_buffer = output_buffer
        self.player = player
        self.text_history_viewer = QListWidget()
        self.dice_roll_viewer = DiceRollViewer(self.dice_manager)
        self.layout = QVBoxLayout()
        self.layout.addWidget(self.text_history_viewer)
        self.layout.addWidget(self.dice_roll_viewer)
        self.layout.addLayout(DiceRollButtonLayout(self.output_buffer, self.player, self.dice_manager))
        self.setLayout(self.layout)
