from PyQt5.QtWidgets import QFormLayout, QWidget, QVBoxLayout

from character.label_edit_widget import ButtonLabelEditWidget


class TalentDisplayLayout(QWidget):
    def __init__(self, parent, talent_group):
        super().__init__(parent)
        self.layout = QVBoxLayout()
        self.parent = parent
        self.character = self.parent.character
        self.line_edits = []
        self.add_line_edits(talent_group)

    def add_line_edits(self, talent_group):
        for talent in talent_group.talents:
            button_label_edit_widget = ButtonLabelEditWidget(self, talent.name, self.character, talent.value, talent, talent.check_against)
            self.layout.addWidget(button_label_edit_widget)
            self.line_edits.append(button_label_edit_widget)
        self.setLayout(self.layout)

