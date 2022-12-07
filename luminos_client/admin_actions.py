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
        self.button = QPushButton()
        self.button.pressed.connect(self.send_update_connected_clients_info)
        self.update_timer = QTimer()
        self.update_timer.timeout.connect(self.send_update_connected_clients_info)
        self.update_timer.start(10000)
        self.layout.addWidget(self.button)
        self.setLayout(self.layout)

    def send_update_connected_clients_info(self):
        self.parent.parent.output_buffer.append(bytes(fix_up_json_string(json.dumps(CommandQueryConnectedClients([]),
                                                                      cls=CommandEncoder)), "UTF-8"))
