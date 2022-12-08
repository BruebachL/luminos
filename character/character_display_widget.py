from PyQt5.QtWidgets import QWidget, QVBoxLayout

from character.character_info_and_base_display_widget import CharacterInfoAndBaseDisplayWidget
from character.character_talent_groups_tabbed_display import CharacterTalentGroupsTabbedDisplay


class CharacterDisplayWidget(QWidget):

    def __init__(self, parent, character):
        super().__init__(parent)
        self.parent = parent
        self.character = character
        self.layout = QVBoxLayout()
        self.info_and_base_display = CharacterInfoAndBaseDisplayWidget(self, self.character)
        self.layout.addWidget(self.info_and_base_display)
        self.talent_tabs = CharacterTalentGroupsTabbedDisplay(self, self.character)
        self.layout.addWidget(self.talent_tabs)

        self.setLayout(self.layout)

