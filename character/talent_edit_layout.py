from PyQt5.QtWidgets import QLineEdit, QComboBox, QHBoxLayout, QPushButton


class TalentEditLayout(QHBoxLayout):

    def __init__(self, parent, character, talent=None):
        super().__init__()
        self.parent = parent
        self.character = character
        self.talent = talent

        # Label edit for the talent name
        self.line_edit_label = QLineEdit()
        if self.talent.name is None:
            self.line_edit_label.setText("")
        else:
            self.line_edit_label.setText(str(self.talent.name))
        self.line_edit_label.textChanged.connect(self.label_changed)
        self.layout().addWidget(self.line_edit_label)
        
        # Label edit for the talent shorthand
        self.line_edit_shorthand = QLineEdit()
        if self.talent.shorthand is None:
            self.line_edit_shorthand.setText("")
        else:
            self.line_edit_shorthand.setText(str(self.talent.shorthand))
        self.line_edit_shorthand.textChanged.connect(self.shorthand_changed)
        self.line_edit_shorthand.setFixedWidth(50)
        self.layout().addWidget(self.line_edit_shorthand)

        # Combo boxes for the talents check against talents
        self.combo_boxes = []
        base_talents = self.character.get_base_talents()
        for i in range(len(self.talent.check_against)):
            combo_box = QComboBox()
            self.combo_boxes.append(combo_box)
            for talent in base_talents:
                combo_box.addItem(talent.name)
            combo_box.setCurrentText(self.talent.check_against[i])
            combo_box.currentTextChanged.connect(self.update_combo)
            combo_box.currentIndexChanged.connect(self.update_combo)
            combo_box.editTextChanged.connect(self.update_combo)
            self.layout().addWidget(combo_box)

        # Label edit for the talents equalizer
        self.line_edit_value = QLineEdit()
        if self.talent.value is None:
            self.line_edit_value.setText("")
        else:
            self.line_edit_value.setText(str(self.talent.value))
        self.line_edit_value.textChanged.connect(self.value_changed)
        self.layout().addWidget(self.line_edit_value)

        # Button to delete the talent

        self.delete_button = QPushButton()
        self.delete_button.setText("-")
        self.delete_button.setFixedWidth(30)
        self.delete_button.clicked.connect(self.delete_talent)
        self.layout().addWidget(self.delete_button)

    def label_changed(self):
        print("Changed name of {} to {}".format(self.talent.name, self.line_edit_label.text()))
        self.talent.name = self.line_edit_label.text()
        self.character.update_talent(self.talent)

    def shorthand_changed(self):
        print("Changed shorthand of {} from {} to {}".format(self.talent.name ,self.talent.shorthand, self.line_edit_shorthand.text()))
        self.talent.shorthand = self.line_edit_shorthand.text()
        self.character.update_talent(self.talent)

    def update_combo(self):
        print("Changing combo boxes for talent {}".format(self.talent.name))
        for i in range(len(self.combo_boxes)):
            print("Changing check against {} to {} for talent {}".format(self.talent.check_against[i], self.combo_boxes[i].currentText(), self.talent.name))
            self.talent.check_against[i] = self.combo_boxes[i].currentText()
        self.character.update_talent(self.talent)

    def value_changed(self):
        print("Changed {} to {} for {}".format(self.talent.value, self.line_edit_value.text(), self.talent.name))
        self.talent.value = self.line_edit_value.text()
        self.character.update_talent(self.talent)

    def delete_talent(self):
        self.character.update_talent(self.talent)
        self.character.delete_talent(self.talent)
        self.parent.update_layout()