import json
import random

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QLineEdit, QPushButton, QWidget, QHBoxLayout, QLabel

from commands.command import CommandRollDice, CommandEncoder
from utils.qt_utils import get_top_most_parent


class ButtonLabelWidget(QWidget):

    def __init__(self, parent, label, character, initial_value=None, talent=None, check_against=None):
        super().__init__(parent)
        self.layout = QHBoxLayout()
        self.parent = parent
        self.character = character
        self.label = label
        self.talent = talent
        self.display_value = QLabel()
        self.check_against = check_against
        self.dice_to_use = []
        for i in range(3):
            if len(self.window().dice_manager.use_dice) > 0:
                self.dice_to_use.append(self.window().dice_manager.use_dice[random.randrange(len(self.window().dice_manager.use_dice))].checksum)
        if initial_value is None:
            initial_value = ""
        check_against_string = ""
        if check_against is not None:
            actual_talents = character.get_talents_to_check_against(check_against)
            for actual_talent in actual_talents:
                check_against_string = check_against_string + actual_talent.shorthand + "/"
        if check_against_string == "":
            check_against_string = talent.shorthand
        else:
            check_against_string = check_against_string[0:-1]
        self.display_value.setText(str(initial_value))
        self.button = QPushButton()
        self.button.setText(label + " (" + check_against_string + ")")
        self.button.clicked.connect(self.on_click)
        self.layout.addWidget(self.button)
        self.layout.addWidget(self.display_value, alignment=Qt.AlignCenter)
        self.setLayout(self.layout)

    def on_click(self):
        talents_to_check = self.character.get_talents_to_check_against(self.check_against)
        talent_names = []
        talent_values = []
        for talent in talents_to_check:
            talent_names.append(talent.name)
            talent_values.append(talent.value)
        command = CommandRollDice(self.character.name, len(talent_values), 20, self.talent.name, talent_values, int(self.display_value.text()), self.dice_to_use)
        self.window().output_buffer.append(bytes(json.dumps(command, cls=CommandEncoder), "UTF-8"))

