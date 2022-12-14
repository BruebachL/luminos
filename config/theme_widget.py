from PyQt5 import QtWidgets, QtCore
from PyQt5.QtWidgets import QWidget, QHBoxLayout, QComboBox
import ui.breeze_resources
from qt_material import apply_stylesheet


class ThemeWidget(QWidget):

    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        self.layout = QHBoxLayout()
        self.combo_box = QComboBox()
        self.valid_themes = {'Default': "", 'Dark': ":/dark/stylesheet.qss", 'Light': ":/light/stylesheet.qss",
                             'Material Dark Amber': 'dark_amber.xml',
                             'Material Dark Blue': 'dark_blue.xml',
                             'Material Dark Cyan': 'dark_cyan.xml',
                             'Material Dark Green': 'dark_lightgreen.xml',
                             'Material Dark Pink': 'dark_pink.xml',
                             'Material Dark Purple': 'dark_purple.xml',
                             'Material Dark Red': 'dark_red.xml',
                             'Material Dark Teal': 'dark_teal.xml',
                             'Material Dark Yellow': 'dark_yellow.xml',
                             'Material Light Amber': 'light_amber.xml',
                             'Material Light Blue': 'light_blue.xml',
                             'Material Light Cyan': 'light_cyan.xml',
                             'Material Light Cyan 500': 'light_cyan_500.xml',
                             'Material Light Green': 'light_lightgreen.xml',
                             'Material Light Pink': 'light_pink.xml',
                             'Material Light Purple': 'light_purple.xml',
                             'Material Light Red': 'light_red.xml',
                             'Material Light Teal': 'light_teal.xml',
                             'Material Light Yellow': 'light_yellow.xml'}
        for valid_theme in self.valid_themes.keys():
            self.combo_box.addItem(valid_theme)
        # TODO: Set this to active theme in config
        self.combo_box.setCurrentText("")
        self.combo_box.currentTextChanged.connect(self.update_combo)
        self.combo_box.currentIndexChanged.connect(self.update_combo)
        self.combo_box.editTextChanged.connect(self.update_combo)
        self.layout.addWidget(self.combo_box)
        # apply_stylesheet()
        self.setLayout(self.layout)

    def update_combo(self):
        match self.combo_box.currentText():
            case 'Default':
                self.set_default_stylesheet("")
            case 'Dark' | 'Light':
                self.set_default_stylesheet(self.read_stylesheet(self.valid_themes[self.combo_box.currentText()]))
            case _ if 'Material' in self.combo_box.currentText():
                apply_stylesheet(QtWidgets.QApplication.instance(),
                                 theme=self.valid_themes[self.combo_box.currentText()])

    def set_default_stylesheet(self, stylesheet_path):
        QtWidgets.QApplication.instance().setStyleSheet(stylesheet_path)

    def read_stylesheet(self, path):
        file = QtCore.QFile(path)
        file.open(QtCore.QFile.ReadOnly | QtCore.QFile.Text)
        stream = QtCore.QTextStream(file)
        return stream.readAll()
