import json

from PyQt5.QtCore import QUrl
from PyQt5.QtMultimedia import QMediaContent, QMediaPlayer
from PyQt5.QtWidgets import QWidget, QPushButton, QComboBox

from commands.command import CommandPlayAudio, CommandEncoder


class AudioDisplayWidget(QWidget):

    def __init__(self, parent, audio_infos):
        super().__init__(parent)
        self.parent = parent
        self.audio_infos = audio_infos
        self.player = QMediaPlayer()
        self.combo_box = QComboBox()

    def play_audio(self, audio_hash):
        audio_to_play = self.parent.get_path_for_hash(audio_hash)
        if audio_to_play is None:
            # audio_to_play = self.request_audio_from_server(audio_hash)
            raise Exception
        media_content = QMediaContent(QUrl.fromLocalFile(audio_to_play))
        self.player.setMedia(media_content)
        self.player.play()

    def add_admin_panel(self):
        if self.window() is not None:
            if self.window().admin_client:
                button = QPushButton()
                button.pressed.connect(self.play_selected_audio)
                self.layout.addWidget(button)
                self.combo_box = QComboBox()
                for audio_info in self.managed_objects:
                    self.combo_box.addItem(audio_info.file_path)
                #self.combo_box.setCurrentText(self.audio_clips[0].file_path)
                #combo_box.currentTextChanged.connect(self.update_combo)
                #combo_box.currentIndexChanged.connect(self.update_combo)
                #combo_box.editTextChanged.connect(self.update_combo)
                self.layout.addWidget(self.combo_box)

    def play_selected_audio(self):
        for audio_info in self.parent.managed_objects:
            if audio_info.file_path == self.combo_box.currentText():
                #self.play_audio(audio_info.file_hash)
                self.window().output_buffer.append(bytes(
                    json.dumps(CommandPlayAudio(audio_info.file_hash, 0),
                               cls=CommandEncoder), "UTF-8"))
        self.update_layout()