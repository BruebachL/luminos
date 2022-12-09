
from PyQt5.QtWidgets import QLineEdit, QFormLayout, QWidget, QVBoxLayout


class CharacterInfoLayout(QWidget):
    def __init__(self, parent, character):
        super().__init__(parent)
        self.layout = QVBoxLayout()
        self.parent = parent
        self.character = character
        self.rows = 2
        self.columns = 10
        self.total_widgets = self.rows * self.columns
        self.add_buttons()
        self.layout.setSpacing(20)
        self.setLayout(self.layout)

    def add_buttons(self):
        self.layout.addWidget(QWidget())
        self.layout.addWidget(QWidget())
        self.layout.addWidget(QWidget())
        self.layout.addWidget(QWidget())
        self.layout.addWidget(QWidget())
        self.layout.addWidget(QWidget())
        name_line_edit = QLineEdit()
        name_line_edit.setText(self.character.name)
        self.layout.addWidget(name_line_edit)
        self.layout.addWidget(QWidget())
        self.layout.addWidget(QWidget())
        age_line_edit = QLineEdit()
        age_line_edit.setText(str(self.character.age))
        self.layout.addWidget(age_line_edit)
        occupation_line_edit = QLineEdit()
        occupation_line_edit.setText(self.character.occupation)
        self.layout.addWidget(QWidget())
        self.layout.addWidget(occupation_line_edit)



