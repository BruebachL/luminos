from PyQt5.QtWidgets import QVBoxLayout, QPushButton

from character.talent import Talent
from character.talent_edit_layout import TalentEditLayout


class TalentGroupEditLayout(QVBoxLayout):
    def __init__(self, character, talent_group):
        super().__init__()
        self.setSpacing(10)
        self.character = character
        self.talent_group = talent_group
        self.line_edits = []
        self.add_line_edits()

    def update_layout(self):
        self.clear_item(self.layout())
        self.add_line_edits()

    def clear_item(self, item):
        if hasattr(item, "layout"):
            if callable(item.layout):
                layout = item.layout()
        else:
            layout = None
        if hasattr(item, "widget"):
            if callable(item.widget):
                widget = item.widget()
        else:
            widget = None
        if widget:
            widget.setParent(None)
        elif layout:
            for i in reversed(range(layout.count())):
                self.clear_item(layout.itemAt(i))

    def add_line_edits(self):
        for talent in self.talent_group.talents:
            talent_edit_layout = TalentEditLayout(self, self.character, talent)
            self.line_edits.append(talent_edit_layout)
            self.layout().addLayout(talent_edit_layout)
        add_talent_button = QPushButton()
        add_talent_button.setText("+")
        add_talent_button.clicked.connect(self.add_talent)
        self.layout().addWidget(add_talent_button)

    def add_talent(self):
        self.character.add_talent(Talent(self.talent_group.name, "", "", ["", "", ""], ""))
        self.update_layout()

