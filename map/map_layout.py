from PyQt5.QtWidgets import QGridLayout, QWidget

from character.image_widget import ImageWidget


class MapLayout(QWidget):

    def __init__(self, map_manager):
        super().__init__()
        self.map_manager = map_manager
        self.image_widget = ImageWidget(self.map_manager.get_active_map())
        self.grid_layout = QGridLayout()
        self.grid_layout.addWidget(self.image_widget)
        self.setLayout(self.grid_layout)
