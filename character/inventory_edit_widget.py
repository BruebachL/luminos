from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel

from character.inventory_item_group_edit_layout import InventoryItemGroupEditLayout


class InventoryEditWidget(QWidget):
    def __init__(self, character):
        super().__init__()
        inventory_item_groups_layout = QVBoxLayout()
        for inventory_item_group in character.inventory.inventory_item_groups:
            print("Added inventory layout")
            item_group_layout = InventoryItemGroupEditLayout(character, inventory_item_group)
            inventory_item_groups_layout.addLayout(item_group_layout)
            inventory_item_groups_layout.addWidget(QLabel(""))
        self.setLayout(inventory_item_groups_layout)