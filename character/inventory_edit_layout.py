from PyQt5.QtWidgets import QWidget, QScrollArea, QVBoxLayout

from character.inventory_edit_widget import InventoryEditWidget


class InventoryEditLayout(QWidget):

    def __init__(self, character):
        super().__init__()
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidget(InventoryEditWidget(character))
        self.setLayout(QVBoxLayout())
        self.layout().addWidget(self.scroll_area)
