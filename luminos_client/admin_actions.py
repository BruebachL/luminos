import json

from PyQt5.QtCore import QTimer
from PyQt5.QtWidgets import QWidget, QGridLayout, QPushButton

from commands.command import CommandEncoder, CommandQueryConnectedClients
from utils.string_utils import fix_up_json_string


class AdminActions(QWidget):

    def __init__(self, parent):
        super().__init__()
        self.parent = parent
        self.layout = QGridLayout()
        self.setLayout(self.layout)
