from PyQt5.QtWidgets import QWidget, QLineEdit, QHBoxLayout

from stingers.stinger_creation_widget import StingerCreationWidget


class StingerControlWidget(QWidget):

    def __init__(self, parent):
        super().__init__(parent)
        self.setParent(parent)
        self.layout = QHBoxLayout()
        self.clue_list = parent.window().clue_manager.clues
        self.audio_list = parent.window().audio_manager.managed_objects
        #self.duration_edit = QLineEdit()
        self.layout.addWidget(StingerCreationWidget(self, self.clue_list, self.audio_list))
        self.setLayout(self.layout)
