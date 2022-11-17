from PyQt5.QtWidgets import QHBoxLayout, QLabel, QLineEdit


class InventoryItemEditLayout(QHBoxLayout):

    def __init__(self, character, item):
        super().__init__()
        self.character = character
        self.item = item
        self.name_label_edit = QLineEdit(str(item.name))
        self.name_label_edit.textChanged.connect(self.name_changed)
        self.description_label_edit = QLineEdit(str(item.description))
        self.description_label_edit.textChanged.connect(self.description_changed)
        self.weight_label_edit = QLineEdit(str(item.weight))
        self.weight_label_edit.textChanged.connect(self.weight_changed)
        self.addWidget(self.name_label_edit)
        self.addWidget(self.description_label_edit)
        self.addWidget(self.weight_label_edit)
        
    def name_changed(self):
        self.item.name = self.name_label_edit.text()
        self.character.inventory.update_item(self.item)
        
    def description_changed(self):
        self.item.description = self.description_label_edit.text()
        self.character.inventory.update_item(self.item)
        
    def weight_changed(self):
        self.item.weight = self.weight_label_edit.text()
        self.character.inventory.update_item(self.item)
