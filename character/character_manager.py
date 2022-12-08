import json
import os

from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QTabWidget

from character.character import decode_character, CharacterEncoder
from character.character_display_widget import CharacterDisplayWidget
from character.character_edit_widget import CharacterEditWidget
from character.character_info_layout import CharacterInfoLayout
from character.inventory_display_layout import InventoryDisplayLayout
from character.inventory_edit_layout import InventoryEditLayout
from character.talent_display_layout import TalentDisplayLayout
from utils.string_utils import fix_up_json_string


class CharacterManager(QWidget):
    def __init__(self, parent, base_path):
        super().__init__(parent)
        self.parent = parent
        self.base_path = base_path

        self.character_sheet_path = self.base_path.joinpath("character_" + self.parent.player + ".json")
        self.character = self.load_character_from_file()

        self.layout = QVBoxLayout()
        self.character_display_widget = CharacterDisplayWidget(self, self.character)

        self.layout.addWidget(self.character_display_widget)
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


    def save_to_file(self):
        try:
            with open(self.character_sheet_path, "w") as file:
                file.write(fix_up_json_string(json.dumps(self.character, cls=CharacterEncoder, separators=(',', ':'), indent=4, ensure_ascii=False)))
                file.close()
        except Exception as e:
            import traceback
            traceback.print_exc(e)
