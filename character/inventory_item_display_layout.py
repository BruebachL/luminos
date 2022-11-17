from PyQt5.QtWidgets import QHBoxLayout, QLabel


class InventoryItemDisplayLayout(QHBoxLayout):

    def __init__(self, item):
        super().__init__()
        self.item = item
        self.addWidget(QLabel(str(item.name)))
        self.addWidget(QLabel(str(item.description)))
        self.addWidget(QLabel(str(item.weight)))
