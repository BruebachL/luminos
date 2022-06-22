
from PyQt5.QtWidgets import QLineEdit, QFormLayout, QWidget


class CharacterInfoLayout(QFormLayout):
    def __init__(self, socket, player):
        super().__init__()
        self.socket = socket
        self.player = player
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
        self.addRow("Name", name_line_edit)
        self.addRow(" ", QWidget())
        self.addRow(" ", QWidget())
        age_line_edit = QLineEdit()
        self.addRow("Age", age_line_edit)
        occupation_line_edit = QLineEdit()
        self.addRow(" ", QWidget())
        self.addRow("Occupation", occupation_line_edit)



