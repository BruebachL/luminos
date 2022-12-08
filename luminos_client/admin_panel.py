from PyQt5.QtWidgets import QWidget, QVBoxLayout

from luminos_client.admin_actions import AdminActions
from luminos_client.tabbed_client_view import TabbedClientView


class AdminPanel(QWidget):

    def __init__(self, parent, connected_clients):
        super().__init__(parent)
        self.parent = parent
        self.connected_clients = connected_clients
        self.layout = QVBoxLayout()
        self.layout.addWidget(AdminActions(self))
        self.layout.addWidget(TabbedClientView(self, self.connected_clients))
        self.setLayout(self.layout)

    def update_layout(self):
        QWidget().setLayout(self.layout)
        new_layout = QVBoxLayout()
        self.layout = new_layout
        self.layout.addWidget(AdminActions(self))
        self.layout.addWidget(TabbedClientView(self, self.connected_clients))
        self.setLayout(new_layout)


