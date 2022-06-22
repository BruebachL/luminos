import json
import random

from PyQt5.QtWidgets import QLineEdit, QPushButton
from commands.command_roll_dice import CommandRollDice, CommandRollDiceEncoder




class ButtonLabelEditWidget:

    def __init__(self, label, output_buffer, dice_manager, character, initial_value=None, talent=None, check_against=None):
        self.output_buffer = output_buffer
        self.dice_manager = dice_manager
        self.character = character
        self.label = label
        self.talent = talent
        self.line_edit = QLineEdit()
        self.check_against = check_against
        self.dice_to_use = []
        for i in range(3):
            if len(self.dice_manager.use_dice) > 0:
                self.dice_to_use.append(self.dice_manager.use_dice[random.randrange(len(self.dice_manager.use_dice))].name)
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
        self.line_edit.setText(str(initial_value))
        self.line_edit.textChanged.connect(self.text_changed)
        self.button = QPushButton()
        self.button.setText(label + " (" + check_against_string + ")")
        self.button.clicked.connect(self.on_click)

    def on_click(self):
        talents_to_check = self.character.get_talents_to_check_against(self.check_against)
        talent_names = []
        talent_values = []
        for talent in talents_to_check:
            talent_names.append(talent.name)
            talent_values.append(talent.value)
        command = CommandRollDice(self.character.name, len(talent_values), 20, self.talent.name, talent_values, int(self.line_edit.text()), self.dice_to_use)
        self.output_buffer.append(bytes(json.dumps(command, cls=CommandRollDiceEncoder), "UTF-8"))

    def text_changed(self):
        self.talent.value = self.line_edit.text()
