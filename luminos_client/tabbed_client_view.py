from PyQt5.QtWidgets import QTabWidget

from luminos_client.connected_client_display import ConnectedClientDisplay


class TabbedClientView(QTabWidget):

    def __init__(self, parent, connected_clients):
        super().__init__(parent)
        self.connected_clients = connected_clients
        for client in self.connected_clients:
            self.addTab(ConnectedClientDisplay(self, client), client.client_friendly_name)