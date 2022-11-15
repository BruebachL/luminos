from PyQt5.QtWidgets import QHBoxLayout, QVBoxLayout

from character.edit_label_widget import EditLabelWidget


class TalentEditLayout(QVBoxLayout):
    def __init__(self, output_buffer, dice_manager, character, talent_group):
        super().__init__()
        self.setSpacing(10)
        self.output_buffer = output_buffer
        self.dice_manager = dice_manager
        self.character = character
        self.line_edits = []
        self.add_line_edits(talent_group)

    def add_line_edits(self, talent_group):
        for talent in talent_group.talents:
            button_label_edit_widget = EditLabelWidget(talent.name, self.output_buffer, self.dice_manager, self.character, talent.name, talent.value, talent, talent.check_against)
            self.layout().addLayout(button_label_edit_widget)

