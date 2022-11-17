from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import QVBoxLayout, QLineEdit, QPushButton

from character.inventory_item import InventoryItem
from character.inventory_item_edit_layout import InventoryItemEditLayout
from utils.string_utils import get_free_name


class InventoryItemGroupEditLayout(QVBoxLayout):

    def __init__(self, parent, character, inventory_item_group):
        super().__init__()
        self.parent = parent
        self.character = character
        self.item_group = inventory_item_group
        self.item_group_name_line_edit = QLineEdit()
        self.add_line_edits()


    def update_layout(self):
        self.parent.update_layout()

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
        self.item_group_name_line_edit = QLineEdit(self.item_group.name)
        font = QFont("Times", 20)
        font.setUnderline(True)
        self.item_group_name_line_edit.setFont(font)
        self.item_group_name_line_edit.textChanged.connect(self.update_item_group_name)
        self.addWidget(self.item_group_name_line_edit)
        for item in self.item_group.items:
            item_layout = InventoryItemEditLayout(self, self.character, item)
            self.addLayout(item_layout)
        add_item_button = QPushButton()
        add_item_button.setText("+")
        add_item_button.clicked.connect(self.add_item)
        self.layout().addWidget(add_item_button)

    def update_item_group_name(self):
        self.item_group.name = self.item_group_name_line_edit.text()
        self.character.inventory.update_item_group(self.item_group)

    def add_item(self):
        name = get_free_name("New Item", (existing_item.name for existing_item in self.item_group.items))
        self.character.inventory.add_item(InventoryItem(self.item_group.name, name, "", 0))
        self.update_layout()
