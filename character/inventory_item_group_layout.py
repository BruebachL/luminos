from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import QVBoxLayout, QLabel

from character.inventory_item_layout import InventoryItemLayout


class InventoryItemGroupLayout(QVBoxLayout):

    def __init__(self, inventory_item_group):
        super().__init__()
        self.item_group = inventory_item_group
        self.item_group_label = QLabel(inventory_item_group.name)
        self.font = QFont("Times", 20)
        self.font.setUnderline(True)
        self.item_group_label.setFont(self.font)
        self.addWidget(self.item_group_label)
        for item in inventory_item_group.items:
            item_layout = InventoryItemLayout(item)
            self.addLayout(item_layout)