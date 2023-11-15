from PyQt5.QtWidgets import QWidget, QVBoxLayout, QPushButton

from config.theme_widget import ThemeWidget


class ConfigWidget(QWidget):

    def __init__(self, parent, managed_objects=None):
        super().__init__(parent)
        self.parent = parent
        self.managed_objects = managed_objects
        self.layout = QVBoxLayout()
        self.theme_selection_widget = ThemeWidget(self)
        self.layout.addWidget(self.theme_selection_widget)
        self.setLayout(self.layout)

