import math
import random

from PyQt5.QtCore import Qt, QSize
from PyQt5.QtGui import QImage, QPainter, QPen, QPainterPath, QFontMetrics, QBrush, QPixmap, QTransform
from PyQt5.QtWidgets import QLabel


class DiceRollWidget(QLabel):

    # def __init__(self, value):
    #     super().__init__()
    #     self.setAlignment(Qt.AlignCenter)
    #     self.setBaseSize(200, 200)
    #     self.setFixedHeight(200)
    #     self.setFixedWidth(200)
    #     self.setScaledContents(False)
    #     self.setFrameStyle(QFrame.StyledPanel)
    #     self.setStyleSheet(
    #         "background-position: center;"
    #         "background-image: url(/home/ascor/PycharmProjects/luminos/D20_icon_scaled.png);"
    #         "background-repeat: no-repeat;"
    #         "border-style: solid;"
    #         "border-width: 0px;"
    #         "border-color: white;"
    #         "color: white;")

    def __init__(self, dice_manager, dice_skin, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.dice_manager = dice_manager
        self.dice_skin = dice_skin
        self.w = 1 / 10
        self.mode = True
        self.brush = None
        self.pen = None
        self.setBrush(Qt.white)
        self.setPen(Qt.black)
        self.setBaseSize(200, 200)
        font = self.font()
        font.setPointSize(20)
        self.setFont(font)
        self.setAlignment(Qt.AlignCenter)
        self.setFixedHeight(200)
        self.setFixedWidth(200)
        self.setScaledContents(False)
        self.setAttribute(Qt.WA_TranslucentBackground, True)

    def scaledOutlineMode(self):
        return self.mode

    def setScaledOutlineMode(self, state):
        self.mode = state

    def outlineThickness(self):
        return self.w * self.font().pointSize() if self.mode else self.w

    def setOutlineThickness(self, value):
        self.w = value

    def setBrush(self, brush):
        if not isinstance(brush, QBrush):
            brush = QBrush(brush)
        self.brush = brush

    def setPen(self, pen):
        if not isinstance(pen, QPen):
            pen = QPen(pen)
        pen.setJoinStyle(Qt.RoundJoin)
        self.pen = pen

    def sizeHint(self):
        w = math.ceil(self.outlineThickness() * 2)
        return super().sizeHint() + QSize(w, w)

    def minimumSizeHint(self):
        w = math.ceil(self.outlineThickness() * 2)
        return super().minimumSizeHint() + QSize(w, w)

    def paintEvent(self, event):
        w = int(self.outlineThickness())
        rect = self.rect()
        metrics = QFontMetrics(self.font())
        tr = metrics.boundingRect(self.text()).adjusted(0, 0, w, w)
        if self.indent() == -1:
            if self.frameWidth():
                indent = (metrics.boundingRect('x').width() + w * 2) / 2
            else:
                indent = w
        else:
            indent = self.indent()

        if self.alignment() & Qt.AlignLeft:
            x = rect.left() + indent - min(metrics.leftBearing(self.text()[0]), 0)
        elif self.alignment() & Qt.AlignRight:
            x = rect.x() + rect.width() - indent - tr.width()
        else:
            x = (rect.width() - tr.width()) / 2

        if self.alignment() & Qt.AlignTop:
            y = rect.top() + indent + metrics.ascent()
        elif self.alignment() & Qt.AlignBottom:
            y = rect.y() + rect.height() - indent - metrics.descent()
        else:
            y = (rect.height() + metrics.ascent() - metrics.descent()) / 2

        path = QPainterPath()
        path.addText(x, y, self.font(), self.text())
        qp = QPainter(self)
        qp.setRenderHint(QPainter.Antialiasing)
        image = QImage()
        if self.dice_skin is None:
            image.load(self.dice_manager.get_dice_for_hash(self.dice_skin).image_path)
        else:
            image.load(self.dice_manager.get_dice_for_hash(self.dice_skin).image_path)
        random_rot = random.randrange(0, 360, 1)
        my_transform = QTransform(1, 0, 0, 1,image.width() / 2, image.height() / 2)
        my_transform.translate(image.width() / 2, image.height() / 2)
        my_transform.rotate(random_rot)
        my_transform.translate(-image.width() / 2, -image.height() / 2)
        pixmap = QPixmap.fromImage(image)
        pixmap_transformed = pixmap.transformed(my_transform)
        xoffset = int((pixmap_transformed.width() - image.width()) / 2)
        yoffset = int((pixmap_transformed.height() - image.height()) / 2)
        rotated = pixmap_transformed.copy(xoffset, yoffset, image.width(), image.height())
        self.setScaledContents(True)
        qp.drawPixmap(0, 0, rotated)
        self.pen.setWidthF(w * 2)
        qp.strokePath(path, self.pen)
        if 1 < self.brush.style() < 15:
            qp.fillPath(path, self.palette().window())
        qp.fillPath(path, self.brush)
