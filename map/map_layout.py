from PyQt5.QtWidgets import QGridLayout, QWidget, QVBoxLayout

from character.image_widget import ImageWidget
from map.map_display_widget import MapDisplayWidget


class MapLayout(QWidget):

    def __init__(self, parent, map_manager):
        super().__init__(parent)
        self.map_manager = map_manager
        self.image_widget = MapDisplayWidget(self.map_manager.get_active_map(), self.map_manager.get_paths_for_overlays())
        print(self.width())
        print(self.height())
        self.grid_layout = QVBoxLayout(self)
        self.grid_layout.addWidget(self.image_widget)
        self.setLayout(self.grid_layout)
        #self.image_widget.setFixedHeight(self.height())
        #self.image_widget.setFixedWidth(self.width())
        print(self.sizeHint().width())
        print(self.sizeHint().height())
        self.repaint()

    def resizeEvent(self, event):
        super().resizeEvent(event)
