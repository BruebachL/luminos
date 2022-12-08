from PyQt5.QtWidgets import QWidget, QLabel, QVBoxLayout

from character.character_display_widget import CharacterDisplayWidget
from luminos_client.connected_client_info_display import ConnectedClientInfoDisplay


class ConnectedClientDisplay(QWidget):

    # client_id, client_friendly_name, version, status

    def __init__(self, parent, client):
        super().__init__(parent)
        self.client = client
        self.client_infos = ConnectedClientInfoDisplay(client)
        self.character_display = CharacterDisplayWidget(self, client.character)
        self.layout = QVBoxLayout()
        self.layout.addWidget(self.client_infos)
        self.layout.addWidget(self.character_display)
        self.setLayout(self.layout)
