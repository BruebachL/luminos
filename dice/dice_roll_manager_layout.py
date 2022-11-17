from PyQt5.QtWidgets import QListWidget, QVBoxLayout
from dice.dice_roll_button_layout import DiceRollButtonLayout
from dice.dice_roll_viewer import DiceRollViewer


class DiceRollManagerLayout(QVBoxLayout):
    def __init__(self, output_buffer, player, dice_manager):
        super().__init__()
        self.dice_manager = dice_manager
        self.output_buffer = output_buffer
        self.player = player
        self.listview = QListWidget()
        self.label = DiceRollViewer(self.dice_manager)
        self.addWidget(self.listview)
        self.addWidget(self.label)
        self.addLayout(DiceRollButtonLayout(self.output_buffer, self.player, self.dice_manager))
