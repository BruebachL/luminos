from PyQt5.QtWidgets import QWidget, QLabel, QVBoxLayout


class ConnectedClientInfoDisplay(QWidget):

    def __init__(self, client):
        super().__init__()
        self.client = client
        self.id_label = QLabel()
        self.id_label.setText(str(client.client_id))
        self.friendly_name_label = QLabel()
        self.friendly_name_label.setText(str(client.client_friendly_name))
        self.version_label = QLabel()
        self.version_label.setText(str(client.version))
        self.status_label = QLabel()
        self.status_label.setText(str(client.status))
        self.layout = QVBoxLayout()
        self.layout.addWidget(self.id_label)
        self.layout.addWidget(self.friendly_name_label)
        self.layout.addWidget(self.version_label)
        self.layout.addWidget(self.status_label)
        self.setLayout(self.layout)
