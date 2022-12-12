from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QTabWidget, QSizePolicy, QInputDialog, QLineEdit

from character.character_info_layout import CharacterInfoLayout
from character.talent_group import TalentGroup
from character.talent_group_edit_layout import TalentGroupEditLayout


class CharacterEditWidget(QWidget):
    def __init__(self, character):
        super().__init__()
        self.character = character
        self.layout = QVBoxLayout()
        self.character_base_and_info_layout = None
        self.character_info_layout = None
        self.size_policy = None
        self.talent_tabs = None
        self.add_talent_group_tab = None
        self.build_layout()
        self.input_dialog = QInputDialog()

    def build_layout(self, select_new_tab = False):
        QWidget().setLayout(self.layout)
        self.layout = QVBoxLayout()
        self.character_base_and_info_layout = QHBoxLayout()
        self.character_info_layout = CharacterInfoLayout(self, self.character)
        self.size_policy = QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.size_policy.setHorizontalStretch(1)
        self.size_policy.setVerticalStretch(1)
        self.character_info_layout.setSizePolicy(self.size_policy)
        self.character_base_and_info_layout.addWidget(self.character_info_layout)
        self.talent_tabs = QTabWidget()
        for talent_group in self.character.talent_groups:
            if talent_group.name == "Base":
                base_talent_layout = TalentGroupEditLayout(self, self.character, talent_group)
                self.character_base_and_info_layout.addLayout(base_talent_layout)
            else:
                talent_group_layout = TalentGroupEditLayout(self, self.character, talent_group)
                talent_group_widget = QWidget()
                talent_group_widget.setLayout(talent_group_layout)
                self.talent_tabs.addTab(talent_group_widget, talent_group.name)
        self.add_talent_group_tab = QWidget()
        self.talent_tabs.addTab(self.add_talent_group_tab, "+")
        self.talent_tabs.currentChanged.connect(self.check_if_create_new_group_tab_was_selected)
        if select_new_tab:
            self.talent_tabs.setCurrentIndex(self.talent_tabs.count() - 2 if self.talent_tabs.count() - 2 > 0 else 0)
        self.layout.addLayout(self.character_base_and_info_layout)
        self.layout.addWidget(self.talent_tabs)
        self.setLayout(self.layout)

    def check_if_create_new_group_tab_was_selected(self):
        if self.talent_tabs.currentWidget() == self.add_talent_group_tab:
            new_talent_group_name = self.input_dialog.getText(self, "Add new Talent Group", "Please enter a name for the new talent group:", QLineEdit.Normal)
            if new_talent_group_name[1]:
                self.character.add_talent_groups([TalentGroup(new_talent_group_name[0], [])])
                self.build_layout(True)
