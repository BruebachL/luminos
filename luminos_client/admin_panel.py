from PyQt5.QtWidgets import QWidget, QVBoxLayout

from luminos_client.admin_actions import AdminActions
from luminos_client.tabbed_client_view import TabbedClientView


class AdminPanel(QWidget):

    def __init__(self, parent, connected_clients):
        super().__init__(parent)
        self.parent = parent
        self.connected_clients = connected_clients
        self.layout = QVBoxLayout()
        self.admin_actions = AdminActions(self)
        self.connected_clients_tabbed_view = TabbedClientView(self, self.connected_clients)
        self.layout.addWidget(self.admin_actions)
        self.layout.addWidget(self.connected_clients_tabbed_view)
        self.setLayout(self.layout)

    def update_layout(self):
        QWidget().setLayout(self.layout)
        new_layout = QVBoxLayout()
        self.layout = new_layout
        self.admin_actions = AdminActions(self)
        self.connected_clients_tabbed_view = TabbedClientView(self, self.connected_clients)
        self.layout.addWidget(self.admin_actions)
        self.layout.addWidget(self.connected_clients_tabbed_view)
        self.setLayout(new_layout)

    def get_selected_client(self):
        return self.connected_clients_tabbed_view.widget(self.connected_clients_tabbed_view.currentIndex()).client


