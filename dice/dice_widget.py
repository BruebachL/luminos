from PyQt5.QtGui import QImage, QPixmap
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QCheckBox, QLineEdit


class DiceWidget(QWidget):
    def __init__(self, dice, dice_manager):
        super().__init__()
        self.dice = dice
        self.dice_manager = dice_manager
        self.layout = QVBoxLayout()
        self.add_dice_layout()
        self.use_checkbox = QCheckBox()
        self.use_checkbox.setChecked(self.dice.use)
        self.use_checkbox.stateChanged.connect(self.use_state_changed)
        self.line_edit = QLineEdit()
        self.line_edit.setText(dice.group)
        self.line_edit.textChanged.connect(self.text_state_changed)
        self.layout.addWidget(self.line_edit)
        self.layout.addWidget(self.use_checkbox)
        self.setLayout(self.layout)

    def add_dice_layout(self):
        image = QImage()
        image.load(self.dice.image_path)
        image_label = QLabel()
        image_label.setPixmap(QPixmap.fromImage(image))
        self.layout.addWidget(image_label)
        name_label = QLabel()
        name_label.setText(self.dice.name)
        self.layout.addWidget(name_label)

    def text_state_changed(self):
        self.dice_manager.dice_group_change(self)

    def use_state_changed(self):
        if self.use_checkbox.isChecked():
            if self.dice not in self.dice_manager.use_dice:
                self.dice_manager.use_dice.append(self.dice)
            self.dice.use = True
        else:
            if self.dice in self.dice_manager.use_dice:
                self.dice_manager.use_dice.remove(self.dice)
            self.dice.use = False
