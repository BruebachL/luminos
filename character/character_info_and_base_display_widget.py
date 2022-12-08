from PyQt5.QtWidgets import QWidget, QHBoxLayout

from character.character_info_layout import CharacterInfoLayout
from character.talent_display_layout import TalentDisplayLayout


class CharacterInfoAndBaseDisplayWidget(QWidget):

    def __init__(self, parent, character):
        super().__init__(parent)
        self.parent = parent
        self.setParent(parent)
        self.character = character
        self.layout = QHBoxLayout()
        self.character_info_layout = CharacterInfoLayout(self, self.character)
        self.layout.addWidget(self.character_info_layout)
        for talent_group in self.character.talent_groups:
            if talent_group.name == "Base":
                base_talent_layout = TalentDisplayLayout(self, talent_group)
                self.layout.addWidget(base_talent_layout)

        self.setLayout(self.layout)
