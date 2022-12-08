import os

from PyQt5.QtWidgets import QPushButton


class OverlayRevealButton(QPushButton):

    def __init__(self, parent, overlay_info):
        super().__init__()
        self.parent = parent
        self.overlay_info = overlay_info

        self.setText('_'.join(os.path.split(self.overlay_info.name)[1].split('_')[4:]))
        self.pressed.connect(self.toggle_overlay)

    def toggle_overlay(self):
        self.parent.toggle_map_overlay(self.overlay_info.file_hash)