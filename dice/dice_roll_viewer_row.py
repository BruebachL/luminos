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
                "background-image: url(" + str(self.dice_manager.base_path.joinpath("dice_tray.png")) + ");"
                "background-position: center;"
                "background-repeat: no-repeat;"
                "border-style: solid;"
                "border-width: 0px;"
                "border-color: white;"
                "color: white;")
        self.current_dice_skin = 0


        for i in range(len(self.dice_rolls)):
            if self.current_dice_skin >= len(self.dice_skins):
                self.current_dice_skin = 0
            layout.addWidget(DiceRollWidget(self.dice_manager, self.dice_skins[self.current_dice_skin], str(self.dice_rolls[i])))
            self.current_dice_skin = self.current_dice_skin + 1
        self.setLayout(layout)
