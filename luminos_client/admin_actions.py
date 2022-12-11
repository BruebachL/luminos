import json

from PyQt5.QtCore import QTimer
from PyQt5.QtWidgets import QWidget, QGridLayout, QPushButton

from commands.command import CommandEncoder, CommandQueryConnectedClients, CommandSendToClient, CommandUpdateClient
from utils.string_utils import fix_up_json_string


class AdminActions(QWidget):

    def __init__(self, parent):
        super().__init__()
        self.parent = parent
        self.layout = QGridLayout()
        self.force_update_button = QPushButton("Force Client Update")
        self.force_update_button.pressed.connect(self.force_client_update)
        self.layout.addWidget(self.force_update_button)
        self.setLayout(self.layout)

    def force_client_update(self):
        self.send_to_connected_client(CommandUpdateClient(None, None))

    def send_to_connected_client(self, cmd):
        connected_client = self.parent.get_selected_client()
        if connected_client is not None:
            self.parent.window().send_to_server(CommandSendToClient(connected_client.client_friendly_name, cmd))
