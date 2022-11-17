
from PyQt5.QtWidgets import QLineEdit, QFormLayout, QWidget


class CharacterInfoLayout(QFormLayout):
    def __init__(self, character):
        super().__init__()
        self.character = character
        self.rows = 2
        self.columns = 10
        self.total_widgets = self.rows * self.columns
        self.add_buttons()

    def add_buttons(self):
        self.addRow(" ", QWidget())
        self.addRow(" ", QWidget())
        self.addRow(" ", QWidget())
        self.addRow(" ", QWidget())
        self.addRow(" ", QWidget())
        self.addRow(" ", QWidget())
        name_line_edit = QLineEdit()
        name_line_edit.setText(self.character.name)
        self.addRow("Name", name_line_edit)
        self.addRow(" ", QWidget())
        self.addRow(" ", QWidget())
        age_line_edit = QLineEdit()
        age_line_edit.setText(str(self.character.age))
        self.addRow("Age", age_line_edit)
        occupation_line_edit = QLineEdit()
        occupation_line_edit.setText(self.character.occupation)
        self.addRow(" ", QWidget())
        self.addRow("Occupation", occupation_line_edit)



