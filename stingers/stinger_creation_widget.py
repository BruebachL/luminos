import json

from PyQt5.QtWidgets import QWidget, QLineEdit, QPushButton, QComboBox, QHBoxLayout

from commands.command import CommandPlayStinger, CommandEncoder


class StingerCreationWidget(QWidget):

    def __init__(self, parent, clue_list, audio_list):
        super().__init__(parent)
        self.setParent(parent)
        self.parent = parent
        self.layout = QHBoxLayout()
        self.clue_list = clue_list
        self.audio_list = audio_list
        self.clue_combobox = QComboBox()
        self.audio_combobox = QComboBox()
        for clue in self.clue_list:
            self.clue_combobox.addItem(clue.file_path, clue)
        for audio in self.audio_list:
            self.audio_combobox.addItem(audio.file_path, audio)
        self.duration_edit = QLineEdit()
        self.add_button = QPushButton()
        self.add_button.pressed.connect(self.play_stinger)
        self.layout.addWidget(self.clue_combobox)
        self.layout.addWidget(self.audio_combobox)
        self.layout.addWidget(self.duration_edit)
        self.layout.addWidget(self.add_button)
        self.setLayout(self.layout)

    def play_stinger(self):
        clue_hash = None
        for clue in self.clue_list:
            if clue.file_path == self.clue_combobox.currentText():
                clue_hash = clue.file_hash
        audio_hash = None
        for audio in self.audio_list:
            if audio.file_path == self.audio_combobox.currentText():
                audio_hash = audio.file_hash
        duration = 3
        try:
            duration = int(self.duration_edit.text())
        except Exception as e:
            pass
        command = CommandPlayStinger(clue_hash, audio_hash, duration)
        self.window().output_buffer.append(bytes(json.dumps(command, cls=CommandEncoder), "UTF-8"))