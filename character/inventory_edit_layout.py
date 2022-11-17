from PyQt5.QtWidgets import QWidget, QScrollArea, QVBoxLayout

from character.inventory_edit_widget import InventoryEditWidget


class InventoryEditLayout(QWidget):

    def __init__(self, character):
        super().__init__()
        self.character = character
        self.scroll_area = QScrollArea()
        self.setLayout(QVBoxLayout())
        self.add_layout_items()

    def add_layout_items(self):
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidget(InventoryEditWidget(self, self.character))
        self.layout().addWidget(self.scroll_area)

    def update_layout(self):
        self.clear_item(self.layout())
        self.add_layout_items()

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
