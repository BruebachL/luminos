from PyQt5.QtWidgets import QHBoxLayout, QLabel, QLineEdit, QPushButton


class InventoryItemEditLayout(QHBoxLayout):

    def __init__(self, parent, character, item):
        super().__init__()
        self.parent = parent
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
        self.delete_button = QPushButton()
        self.delete_button.setText("-")
        self.delete_button.setFixedWidth(30)
        self.delete_button.clicked.connect(self.delete_item)
        self.addWidget(self.delete_button)
        
    def name_changed(self):
        self.item.name = self.name_label_edit.text()
        self.character.inventory.update_item(self.item)
        
    def description_changed(self):
        self.item.description = self.description_label_edit.text()
        self.character.inventory.update_item(self.item)
        
    def weight_changed(self):
        self.item.weight = self.weight_label_edit.text()
        self.character.inventory.update_item(self.item)

    def delete_item(self):
        self.character.inventory.update_item(self.item)
        self.character.inventory.delete_item(self.item)
        self.parent.update_layout()
