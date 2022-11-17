from PyQt5.QtGui import QPixmap, QImage
from PyQt5.QtWidgets import QLabel, QMenu


class ImageWidget(QLabel):
    def __init__(self, image):
        super().__init__()
        self.set_image(image)
        self.setScaledContents(True)

    def set_image(self, image_path):
        with open(image_path, "rb") as file:
            image = QImage()
            image.loadFromData(file.read())
            self.setPixmap(QPixmap.fromImage(image))