import json
import os

from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QTabWidget

from character.character import decode_character
from character.character_edit_widget import CharacterEditWidget
from character.character_info_layout import CharacterInfoLayout
from character.inventory_display_layout import InventoryDisplayLayout
from character.inventory_edit_layout import InventoryEditLayout
from character.talent_display_layout import TalentDisplayLayout


class CharacterManager(QWidget):
    def __init__(self, parent, base_path):
        super().__init__(parent)
        self.parent = parent
        self.base_path = base_path

        self.character_sheet_path = self.base_path.joinpath("character_" + self.parent.player + ".json")
        self.character = self.load_character_from_file()

        self.layout = QVBoxLayout()
        character_base_and_info_layout = QHBoxLayout()
        character_info_layout = CharacterInfoLayout(self.character)
        character_base_and_info_layout.addLayout(character_info_layout)

        character_base_and_info_widget = QWidget()
        talent_tabs = QTabWidget()
        for talent_group in self.character.talent_groups:
            if talent_group.name == "Base":
                base_talent_layout = TalentDisplayLayout(self, talent_group)
                character_base_and_info_layout.addLayout(base_talent_layout)
            else:
                talent_group_layout = TalentDisplayLayout(self, talent_group)
                talent_group_widget = QWidget(talent_tabs)
                talent_group_widget.setLayout(talent_group_layout)
                talent_tabs.addTab(talent_group_widget, talent_group.name)
        character_base_and_info_widget.setLayout(character_base_and_info_layout)
        self.layout.addWidget(character_base_and_info_widget)
        self.layout.addWidget(talent_tabs)
        self.setLayout(self.layout)

    def generate_ui_tabs(self, parent_layout):
        parent_layout.addTab(self, "Character")
        if self.parent.admin_client:
            parent_layout.addTab(self.character_edit_tab_ui(), "Character Edit")
        parent_layout.addTab(self.character_inventory_tab_ui(), "Inventory")
        if self.parent.admin_client:
            parent_layout.addTab(self.character_inventory_edit_tab_ui(), "Inventory Edit")
        return parent_layout


    def character_edit_tab_ui(self):
        return CharacterEditWidget(self.character)


    def character_inventory_tab_ui(self):
        return InventoryDisplayLayout(self.character)


    def character_inventory_edit_tab_ui(self):
        return InventoryEditLayout(self.character)


    def load_character_from_file(self):
        if not os.path.exists(self.character_sheet_path):
            with open(self.character_sheet_path, "w+") as file:
                with open(self.base_path.joinpath("character.json")) as default_file:
                    file.write(default_file.read())
        character_to_read = open(self.character_sheet_path, "r")
        character_json = character_to_read.read()
        character_to_read.close()
        return json.loads(str(character_json), object_hook=decode_character)


    def save_to_file(self, character_to_write):
        try:
            with open(self.character_sheet_path, "w") as file:
                file.write(character_to_write)
                file.close()
        except Exception as e:
            import traceback
            traceback.print_exc(e)
