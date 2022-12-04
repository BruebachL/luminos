from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPixmap, QImage, QPainter
from PyQt5.QtWidgets import QLabel


class ImageWidget(QLabel):
    def __init__(self, base_image_path):
        super().__init__()
        self.base_image_path = base_image_path
        self.base_image = None
        self.load_images()
        self.setScaledContents(True)

    def load_images(self):
        with open(self.base_image_path, "rb") as file:
            image = QImage()
            image.loadFromData(file.read())
            self.base_image = QPixmap.fromImage(image)

    def paintEvent(self, event):
        # force alpha by filling pixmap with transparency
        painter = QPainter(self)
        painter.drawPixmap(0, 0, self.base_image)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.base_image = self.base_image.scaled(self.width(), self.height(), Qt.KeepAspectRatio)