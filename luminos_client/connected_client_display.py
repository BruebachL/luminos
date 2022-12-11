from PyQt5.QtWidgets import QWidget, QLabel, QVBoxLayout, QTabWidget

from character.character_display_widget import CharacterDisplayWidget
from character.character_edit_widget import CharacterEditWidget
from luminos_client.connected_client_info_display import ConnectedClientInfoDisplay


class ConnectedClientDisplay(QWidget):

    # client_id, client_friendly_name, version, status

    def __init__(self, parent, client):
        super().__init__(parent)
        self.client = client
        self.client_infos = ConnectedClientInfoDisplay(client)
        if client.character is not None:
            self.character_tabs = QTabWidget()
            self.character_display = CharacterDisplayWidget(self, client.character)
            self.character_edit = CharacterEditWidget(client.character)
        self.layout = QVBoxLayout()
        self.layout.addWidget(self.client_infos)
        if client.character is not None:
            self.character_tabs.addTab(self.character_display, "Character")
            self.character_tabs.addTab(self.character_edit, "Character Edit")
            self.layout.addWidget(self.character_tabs)
        self.setLayout(self.layout)
