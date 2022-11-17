from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QTabWidget

from character.character_info_layout import CharacterInfoLayout
from character.talent_group_edit_layout import TalentGroupEditLayout


class CharacterEditWidget(QWidget):
    def __init__(self, character):
        super().__init__()
        encasing_layout = QVBoxLayout()
        character_base_and_info_layout = QHBoxLayout()
        character_info_layout = CharacterInfoLayout(character)
        character_base_and_info_layout.addLayout(character_info_layout)
        talent_tabs = QTabWidget()
        for talent_group in character.talent_groups:
            if talent_group.name == "Base":
                base_talent_layout = TalentGroupEditLayout(character, talent_group)
                character_base_and_info_layout.addLayout(base_talent_layout)
            else:
                talent_group_layout = TalentGroupEditLayout(character, talent_group)
                talent_group_widget = QWidget()
                talent_group_widget.setLayout(talent_group_layout)
                talent_tabs.addTab(talent_group_widget, talent_group.name)
        encasing_layout.addLayout(character_base_and_info_layout)
        encasing_layout.addWidget(talent_tabs)
        self.setLayout(encasing_layout)