import hashlib
import json
import os
from os import listdir
from os.path import isfile, join
from pathlib import Path

from PyQt5.QtCore import QUrl
from PyQt5.QtMultimedia import QMediaPlayer, QMediaContent
from PyQt5.QtMultimediaWidgets import QVideoWidget
from PyQt5.QtWidgets import QWidget, QGridLayout, QPushButton, QComboBox, QLineEdit

from video.video_info import VideoInfo, decode_video_info, VideoInfoEncoder
from commands.command import CommandEncoder, CommandPlayVideo


class VideoManager(QWidget):

    def __init__(self, parent, basePath):
        super().__init__(parent)
        self.parent = parent
        self.base_path = Path(basePath)
        self.base_resource_path = Path.joinpath(self.base_path, Path("resources")).joinpath(Path("video"))
        if not os.path.exists(self.base_resource_path):
            os.mkdir(self.base_resource_path)
        self.video_info_config_file = Path.joinpath(self.base_path, "video.json")
        if not os.path.exists(self.video_info_config_file):
            try:
                open(self.video_info_config_file, 'x')
            except FileExistsError as e:
                pass
        self.file_hash_map = self.populate_file_hash_map()
        self.player = QMediaPlayer()
        self.video_widget = QVideoWidget()
        self.media_content = None
        self.player.setVideoOutput(self.video_widget)
        self.video_clips = []
        self.read_from_file()
        self.detect_unknown_videos()
        self.layout = QGridLayout()
        self.combo_box = QComboBox()
        self.duration = QLineEdit()
        self.add_admin_panel()
        self.layout.addWidget(self.video_widget)
        self.setLayout(self.layout)

    def play_video(self, video_hash):
        video_to_play = self.get_path_for_hash(video_hash)
        if video_to_play is None:
            # video_to_play = self.request_video_from_server(video_hash)
            raise Exception
        self.media_content = QMediaContent(QUrl.fromLocalFile(video_to_play))
        self.player.setMedia(self.media_content)
        self.player.play()

    def add_admin_panel(self):
        if self.parent is not None:
            if self.parent.admin_client:
                button = QPushButton()
                button.pressed.connect(self.play_selected_video)
                self.layout.addWidget(button)
                self.combo_box = QComboBox()
                for video_info in self.video_clips:
                    self.combo_box.addItem(video_info.file_path)
                self.duration = QLineEdit()
                self.duration.setText("0")
                #self.combo_box.setCurrentText(self.video_clips[0].file_path)
                #combo_box.currentTextChanged.connect(self.update_combo)
                #combo_box.currentIndexChanged.connect(self.update_combo)
                #combo_box.editTextChanged.connect(self.update_combo)
                self.layout.addWidget(self.combo_box)
                self.layout.addWidget(self.duration)

    def play_selected_video(self):
        try:
            duration = int(self.duration.text())
        except Exception as e:
            duration = 10
        for video_info in self.video_clips:
            if video_info.file_path == self.combo_box.currentText():
                self.parent.output_buffer.append(bytes(
                    json.dumps(CommandPlayVideo(video_info.file_hash, duration),
                               cls=CommandEncoder), "UTF-8"))
        self.update_layout()

    def update_layout(self):
        QWidget().setLayout(self.layout)
        self.layout = QGridLayout()
        self.combo_box = QComboBox()
        self.add_admin_panel()
        self.video_widget = QVideoWidget()
        self.player.setVideoOutput(self.video_widget)
        self.layout.addWidget(self.video_widget)
        self.setLayout(self.layout)
        self.repaint()


    def get_video_info_for_hash(self, file_hash):
        for video_info in self.video_clips:
            if video_info.file_hash == file_hash:
                return video_info
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

    def detect_unknown_videos(self):
        for file_hash in self.file_hash_map.keys():
            if file_hash not in (video_info.file_hash for video_info in self.video_clips):
                self.video_clips.append(VideoInfo(file_hash, self.file_hash_map[file_hash], "Unknown"))

    def read_from_file(self):
        file = open(self.video_info_config_file, "r")
        lines = file.readlines()
        for line in lines:
            self.video_clips.append(json.loads(line, object_hook=decode_video_info))

    def save_to_file(self):
        file = open(self.video_info_config_file, "w")
        for video_info in self.video_clips:
            if video_info is not None:
                file.write(json.dumps(video_info, cls=VideoInfoEncoder) + "\n")
        file.close()
