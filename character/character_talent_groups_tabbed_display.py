from PyQt5.QtWidgets import QTabWidget, QWidget

from character.talent_display_layout import TalentDisplayLayout


class CharacterTalentGroupsTabbedDisplay(QTabWidget):

    def __init__(self, parent, character):
        super().__init__(parent)
        self.parent = parent
        self.character = character
        for talent_group in self.character.talent_groups:
            if not talent_group.name == "Base":
                talent_group_widget = TalentDisplayLayout(self, talent_group)
                self.addTab(talent_group_widget, talent_group.name)