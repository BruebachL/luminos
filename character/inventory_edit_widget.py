from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel

from character.inventory_item_group_edit_layout import InventoryItemGroupEditLayout


class InventoryEditWidget(QWidget):
    def __init__(self, parent, character):
        super().__init__()
        self.parent = parent
        self.character = character
        self.inventory_item_groups_layout = QVBoxLayout()
        self.add_layout_items()
        self.setLayout(self.inventory_item_groups_layout)


    def add_layout_items(self):
        for inventory_item_group in self.character.inventory.inventory_item_groups:
            item_group_layout = InventoryItemGroupEditLayout(self, self.character, inventory_item_group)
            self.inventory_item_groups_layout.addLayout(item_group_layout)
            self.inventory_item_groups_layout.addWidget(QLabel(""))


    def update_layout(self):
        #self.clear_item(self.layout())
        #self.add_layout_items()
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