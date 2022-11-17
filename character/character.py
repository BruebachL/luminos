import json

from character.inventory import decode_inventory, InventoryEncoder, Inventory
from character.inventory_item import InventoryItem
from character.inventory_item_group import InventoryItemGroup
from character.talent import decode_talent
from character.talent_group import TalentGroup, TalentGroupEncoder, decode_talent_group
from utils.string_utils import fix_up_json_string


def decode_character_sheet(sheet):
    if sheet['class'] == "talent_group":
        return json.loads(str(sheet).replace('"', "%").replace("\'", "\""), object_hook=decode_talent_group)
    if sheet['class'] == "talent":
        return json.loads(str(sheet).replace('%', '"').replace("\'", "\""), object_hook=decode_talent)
    return sheet


class Character:
    def __init__(self, name, age, occupation, talent_groups, inventory):
        self.name = name
        self.age = age
        self.occupation = occupation
        self.talent_groups = []
        self.fields = []
        self.inventory = inventory
        self.add_talent_groups(talent_groups)

    def add_talent_groups(self, groups):
        for group in groups:
            if isinstance(group, TalentGroup):
                self.talent_groups.append(group)
            else:
                self.talent_groups.append(TalentGroup(group[0], group[1]))

    def get_talents_to_check_against(self, to_check_against):
        talents = []
        for check_against in to_check_against:
            for group in self.talent_groups:
                for talent in group.talents:
                    if talent.name == check_against:
                        talents.append(talent)
        return talents

    #TODO: I'm honestly not sure if we need all these functions to add/update in such a convoluted way.

    def get_talent_index_by_name(self, talent_to_get):
        for i in range(len(self.talent_groups)):
            if self.talent_groups[i].name == talent_to_get.group:
                for j in range(len(self.talent_groups[i].talents)):
                    if self.talent_groups[i].talents[j].name == talent_to_get.name:
                        return i, j

    def add_talent(self, talent_to_add):
        found = False
        for talent_group in self.talent_groups:
            if talent_group.name == talent_to_add.group:
                talent_group.talents.append(talent_to_add)
                found = True
        if not found:
            self.talent_groups.append(TalentGroup(talent_to_add.group, [talent_to_add]))

    def update_talent(self, talent_to_update):
        old_talent_group, old_talent_index = self.get_talent_index_by_name(talent_to_update)
        self.talent_groups[old_talent_group].talents[old_talent_index] = talent_to_update

    def delete_talent(self, talent_to_delete):
        for talent_group in self.talent_groups:
            for talent in talent_group.talents:
                if talent.equals(talent_to_delete):
                    talent_group.talents.remove(talent)
                    break

    def get_base_talents(self):
        base_talents = []
        for talent_group in self.talent_groups:
            if talent_group.name == "Base":
                for talent in talent_group.talents:
                    base_talents.append(talent)
        return base_talents

def decode_character(dct):
    if dct['class'] == "character":
        talent_groups = []
        for talent_group in dct['talent_groups']:
            print(talent_group)
            talent_groups.append(json.loads(str(talent_group).replace("'", '"'), object_hook=decode_talent_group))
        return Character(dct['name'], dct['age'], dct['occupation'], talent_groups, json.loads(str(dct['inventory']).replace("'", '"'), object_hook=decode_inventory))
    return dct


class CharacterEncoder(json.JSONEncoder):

    def default(self, c):
        if isinstance(c, Character):
            json_talents = []
            for talent_group in c.talent_groups:
                json_talents.append(fix_up_json_string(json.dumps(talent_group, cls=TalentGroupEncoder, ensure_ascii=False)))
            return {"class": 'character', "name": c.name, "age": c.age, "occupation": c.occupation,
                    "inventory": fix_up_json_string(json.dumps(c.inventory, cls=InventoryEncoder, ensure_ascii=False)),
                    "talent_groups": json_talents}
        else:
            return super().default(c)
