from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPixmap, QImage, QPainter
from PyQt5.QtWidgets import QLabel


class MapDisplayWidget(QLabel):
    def __init__(self, base_image_path, overlay_paths=None):
        super().__init__()
        self.base_image_path = base_image_path
        if overlay_paths is None:
            overlay_paths = []
        self.overlay_paths = overlay_paths
        self.base_image = None
        self.overlays = []
        self.load_images()
        self.setScaledContents(True)

    def load_images(self):
        with open(self.base_image_path, "rb") as file:
            image = QImage()
            image.loadFromData(file.read())
            self.base_image = QPixmap.fromImage(image)
        for overlay_path in self.overlay_paths:
            with open(overlay_path, "rb") as file:
                image = QImage()
                image.loadFromData(file.read())
                self.overlays.append(QPixmap.fromImage(image))

    def paintEvent(self, event):
        # force alpha by filling pixmap with transparency
        painter = QPainter(self)
        painter.drawPixmap(0, 0, self.base_image)
        for overlay_image in self.overlays:
            painter.drawPixmap(0,0, overlay_image)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.base_image = self.base_image.scaled(self.parent().width(), self.parent().height(), Qt.KeepAspectRatio)
        resized_overlays = []
        for image in self.overlays:
            resized_overlays.append(image.scaled(self.parent().width(), self.parent().height(), Qt.KeepAspectRatio))
        self.overlays = resized_overlays