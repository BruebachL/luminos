import json
import random

from PyQt5.QtWidgets import QLineEdit, QPushButton, QComboBox, QHBoxLayout

from commands.command import CommandRollDice, CommandEncoder


class EditLabelWidget(QHBoxLayout):

    def __init__(self, label, output_buffer, dice_manager, character,
                 initial_label=None, initial_value=None, talent=None, check_against=None):
        super().__init__()
        self.output_buffer = output_buffer
        self.dice_manager = dice_manager
        self.character = character
        self.label = label
        self.talent = talent

        self.line_edit_label = QLineEdit()
        if initial_label is None:
            initial_label = ""
        self.line_edit_label.setText(str(initial_label))
        self.line_edit_label.textChanged.connect(self.label_changed)
        self.layout().addWidget(self.line_edit_label)

        self.combo_boxes = []
        base_talents = self.character.get_base_talents()
        for i in range(len(check_against)):
            combo_box = QComboBox()
            self.combo_boxes.append(combo_box)
            for talent in base_talents:
                combo_box.addItem(talent.name)
            combo_box.setCurrentText(check_against[i])
            combo_box.currentTextChanged.connect(self.update_combo)
            combo_box.currentIndexChanged.connect(self.update_combo)
            combo_box.editTextChanged.connect(self.update_combo)
            self.layout().addWidget(combo_box)

        self.line_edit_value = QLineEdit()
        if initial_value is None:
            initial_value = ""
        self.line_edit_value.setText(str(initial_value))
        self.line_edit_value.textChanged.connect(self.value_changed)
        self.layout().addWidget(self.line_edit_value)
        self.check_against = check_against

    def value_changed(self):
        print("Update value fired")
        self.talent.value = self.line_edit_value.text()
        self.character.update_talent(self.talent)

    def label_changed(self):
        print("Update label fired")
        self.talent.name = self.line_edit_label.text()
        self.character.update_talent(self.talent)

    def update_combo(self):
        print("Update fired")
        for i in range(len(self.combo_boxes)):
            self.talent.check_against[i] = self.combo_boxes[i].currentText()
        self.character.update_talent(self.talent)
