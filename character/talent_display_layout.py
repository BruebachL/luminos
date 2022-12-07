from PyQt5.QtWidgets import QFormLayout, QWidget

from character.label_edit_widget import ButtonLabelEditWidget


class TalentDisplayLayout(QFormLayout):
    def __init__(self, parent, talent_group):
        super().__init__()
        self.setSpacing(10)
        self.parent = parent
        self.character = self.parent.character
        self.line_edits = []
        self.add_line_edits(talent_group)

    def add_line_edits(self, talent_group):
        self.addRow(talent_group.name, QWidget())
        for talent in talent_group.talents:
            button_label_edit_widget = ButtonLabelEditWidget(self, talent.name, self.character, talent.value, talent, talent.check_against)
            self.addRow(button_label_edit_widget.button, button_label_edit_widget.line_edit)
            self.line_edits.append(button_label_edit_widget)

