from PyQt5.QtWidgets import QWidget, QGridLayout

from dice.dice_widget import DiceWidget


class DiceGroupWidget(QWidget):

    def __init__(self, dice_group, dice_manager):
        super().__init__()
        self.layout = QGridLayout()
        self.dice_manager = dice_manager
        self.dice_group = dice_group
        self.width = int(self.width() / 200)
        height = int(self.height() / 200)
        self.row_counter = 0
        self.column_counter = 0
        self.add_dice_widgets()
        self.setLayout(self.layout)

    def add_dice_widget(self, dice):
        self.layout.addWidget(DiceWidget(dice, self.dice_manager), self.row_counter, self.column_counter)
        if self.column_counter == self.width:
            self.row_counter = self.row_counter + 1
            self.column_counter = 0
        else:
            self.column_counter = self.column_counter + 1

    def add_dice_widgets(self):
        for dice in self.dice_group.dice:
            self.add_dice_widget(dice)
