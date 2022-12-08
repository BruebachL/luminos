import hashlib
import json
import os
from os import listdir
from os.path import isfile, join
from pathlib import Path

from PyQt5.QtCore import QUrl
from PyQt5.QtMultimedia import QMediaPlayer, QMediaContent
from PyQt5.QtWidgets import QWidget, QGridLayout, QPushButton, QComboBox

from audio.audio_info import AudioInfo, decode_audio_info, AudioInfoEncoder
from commands.command import CommandEncoder, CommandPlayAudio


class AudioManager(QWidget):

    def __init__(self, parent, basePath):
        super().__init__(parent)
        self.parent = parent
        self.base_path = Path(basePath)
        self.base_resource_path = Path.joinpath(self.base_path, Path("resources")).joinpath(Path("audio"))
        if not os.path.exists(self.base_resource_path):
            os.mkdir(self.base_resource_path)
        self.audio_info_config_file = Path.joinpath(self.base_path, "audio.json")
        if not os.path.exists(self.audio_info_config_file):
            try:
                open(self.audio_info_config_file, 'x')
            except FileExistsError as e:
                pass
        self.file_hash_map = self.populate_file_hash_map()
        self.player = QMediaPlayer()

        self.audio_clips = []
        self.read_from_file()
        self.detect_unknown_audios()
        self.layout = QGridLayout()
        self.combo_box = QComboBox()
        self.add_admin_panel()
        self.setLayout(self.layout)

    def play_audio(self, audio_hash):
        audio_to_play = self.get_path_for_hash(audio_hash)
        if audio_to_play is None:
            # audio_to_play = self.request_audio_from_server(audio_hash)
            raise Exception
        media_content = QMediaContent(QUrl.fromLocalFile(audio_to_play))
        self.player.setMedia(media_content)
        self.player.play()

    def add_admin_panel(self):
        if self.parent is not None:
            if self.parent.admin_client:
                button = QPushButton()
                button.pressed.connect(self.play_selected_audio)
                self.layout.addWidget(button)
                self.combo_box = QComboBox()
                for audio_info in self.audio_clips:
                    self.combo_box.addItem(audio_info.file_path)
                #self.combo_box.setCurrentText(self.audio_clips[0].file_path)
                #combo_box.currentTextChanged.connect(self.update_combo)
                #combo_box.currentIndexChanged.connect(self.update_combo)
                #combo_box.editTextChanged.connect(self.update_combo)
                self.layout.addWidget(self.combo_box)

    def play_selected_audio(self):
        for audio_info in self.audio_clips:
            if audio_info.file_path == self.combo_box.currentText():
                #self.play_audio(audio_info.file_hash)
                self.parent.output_buffer.append(bytes(
                    json.dumps(CommandPlayAudio(audio_info.file_hash, 0),
                               cls=CommandEncoder), "UTF-8"))
        self.update_layout()

    def update_layout(self):
        QWidget().setLayout(self.layout)
        self.layout = QGridLayout()
        self.combo_box = QComboBox()
        self.add_admin_panel()
        self.setLayout(self.layout)
        self.repaint()


    def get_audio_info_for_hash(self, file_hash):
        for audio_info in self.audio_clips:
            if audio_info.file_hash == file_hash:
                return audio_info
        return None

    def get_path_for_hash(self, file_hash):
        if file_hash in self.file_hash_map.keys():
            return self.file_hash_map[file_hash]
        return None

    def populate_file_hash_map(self):
        file_hash_map = {}
        onlyfiles = [join(self.base_resource_path, f) for f in listdir(self.base_resource_path) if isfile(join(self.base_resource_path, f))]
        for file_path in onlyfiles:
            with open(file_path, 'rb') as file:
                file_hash_map[hashlib.sha256(file.read()).hexdigest()] = str(file_path)
        return file_hash_map

    def detect_unknown_audios(self):
        for file_hash in self.file_hash_map.keys():
            if file_hash not in (audio_info.file_hash for audio_info in self.audio_clips):
                self.audio_clips.append(AudioInfo(file_hash, self.file_hash_map[file_hash], "Unknown"))

    def read_from_file(self):
        file = open(self.audio_info_config_file, "r")
        lines = file.readlines()
        for line in lines:
            self.audio_clips.append(json.loads(line, object_hook=decode_audio_info))

    def save_to_file(self):
        file = open(self.audio_info_config_file, "w")
        for audio_info in self.audio_clips:
            if audio_info is not None:
                file.write(json.dumps(audio_info, cls=AudioInfoEncoder) + "\n")
        file.close()
