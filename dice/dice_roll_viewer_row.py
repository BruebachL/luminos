from pathlib import Path

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QWidget, QHBoxLayout

from dice.dice_roll_widget import DiceRollWidget


class DiceRollViewerRow(QWidget):

    def __init__(self, dice_rolls, dice_skins, dice_manager):
        super().__init__()
        self.dice_manager = dice_manager
        self.dice_rolls = dice_rolls
        self.dice_skins = dice_skins
        layout = QHBoxLayout()
        self.setAttribute(Qt.WA_StyledBackground, True)
        self.setStyleSheet(
                "background-image: url(" + str(Path(self.dice_manager.base_path).joinpath("dice_tray.png")) + ");"
                "background-position: center;"
                "background-repeat: no-repeat;"
                "border-style: solid;"
                "border-width: 0px;"
                "border-color: white;"
                "color: white;")
        for i in range(len(self.dice_rolls)):
            layout.addWidget(DiceRollWidget(self.dice_manager, self.dice_skins[i], str(self.dice_rolls[i])))
        self.setLayout(layout)
