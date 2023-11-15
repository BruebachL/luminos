import json

from PyQt5.QtCore import QUrl
from PyQt5.QtMultimedia import QMediaPlayer, QMediaContent
from PyQt5.QtWidgets import QWidget, QGridLayout, QPushButton, QComboBox

from commands.command import CommandEncoder, CommandPlayAudio
from manager.abstract_manager import AbstractManager


class AudioManager(AbstractManager):

    def __init__(self, parent, basePath, manager_name, display_widget_class, managed_object_class, encoder, decoder):
        super().__init__(parent, basePath, manager_name, display_widget_class, managed_object_class, encoder, decoder)
        self.update_layout()

    def update_layout(self):
        QWidget().setLayout(self.layout)
        self.layout = QGridLayout()
        self.combo_box = QComboBox()
        #self.add_admin_panel()
        self.setLayout(self.layout)
        self.repaint()


    def gather_additional_object_info(self):
        return {"display_name": "Unknown."}
