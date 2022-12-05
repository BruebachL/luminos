from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPixmap, QImage, QPainter
from PyQt5.QtWidgets import QLabel


class MapDisplayWidget(QLabel):
    def __init__(self, base_map_info):
        super().__init__()
        self.base_map_info = base_map_info
        self.base_image = None
        self.overlays = {}
        self.load_images()
        self.setScaledContents(True)

    def load_images(self):
        with open(self.base_map_info.name, "rb") as file:
            image = QImage()
            image.loadFromData(file.read())
            self.base_image = QPixmap.fromImage(image)
        for overlay in self.base_map_info.overlays:
            with open(overlay.name, "rb") as file:
                image = QImage()
                image.loadFromData(file.read())
                self.overlays[overlay] = (QPixmap.fromImage(image))

    def paintEvent(self, event):
        # force alpha by filling pixmap with transparency
        painter = QPainter(self)
        painter.drawPixmap(0, 0, self.base_image)
        for overlay in self.base_map_info.overlays:
            if overlay.revealed is True:
                painter.drawPixmap(0,0, self.overlays[overlay])

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.base_image = self.base_image.scaled(self.parent().width(), self.parent().height(), Qt.KeepAspectRatio)
        for image in self.overlays:
            self.overlays[image] = self.overlays[image].scaled(self.parent().width(), self.parent().height(), Qt.KeepAspectRatio)
