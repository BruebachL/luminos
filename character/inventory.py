import json

from character.inventory_item_group import decode_inventory_item_group, InventoryItemGroupEncoder, InventoryItemGroup
from utils.string_utils import fix_up_json_string


class Inventory:

    def __init__(self, inventory_item_groups=None):
        if inventory_item_groups is None:
            inventory_item_groups = []
        self.inventory_item_groups = inventory_item_groups
        
    def get_item_index_by_name(self, item_to_get):
        for i in range(len(self.inventory_item_groups)):
            if self.inventory_item_groups[i].name == item_to_get.group:
                for j in range(len(self.inventory_item_groups[i].items)):
                    if self.inventory_item_groups[i].items[j].name == item_to_get.name:
                        return i, j
        
    def add_item(self, item_to_add):
        found = False
        for item_group in self.inventory_item_groups:
            if item_group.name == item_to_add.group:
                item_group.items.append(item_to_add)
                found = True
        if not found:
            self.inventory_item_groups.append(InventoryItemGroup(item_to_add.group, [item_to_add]))

    def update_item(self, item_to_update):
        old_item_group, old_item_index = self.get_item_index_by_name(item_to_update)
        self.inventory_item_groups[old_item_group].items[old_item_index] = item_to_update

    def delete_item(self, item_to_delete):
        for item_group in self.inventory_item_groups:
            for item in item_group.items:
                if item.equals(item_to_delete):
                    item_group.items.remove(item)
                    break

    def get_item_group_index_by_name(self, item_group_to_get):
        for i in range(len(self.inventory_item_groups)):
            if self.inventory_item_groups[i].name == item_group_to_get.name:
                return i

    def add_item_group_group(self, item_group_to_add):
        if item_group_to_add.name not in (item_group.name for item_group in self.inventory_item_groups):
            self.inventory_item_groups.append(item_group_to_add)

    def update_item_group(self, item_group_to_update):
        old_item_group_index = self.get_item_group_index_by_name(item_group_to_update)
        for item in item_group_to_update.items:
            item.group = item_group_to_update.name
        self.inventory_item_groups[old_item_group_index] = item_group_to_update

    def delete_item_group(self, item_group_to_delete):
        for item_group in self.inventory_item_groups:
            if item_group.equals(item_group_to_delete):
                self.inventory_item_groups.remove(item_group)


def decode_inventory(dct):
    if dct['class'] == "inventory":
        inventory_item_groups = []
        for item_group in dct['inventory_item_groups']:
            inventory_item_groups.append(json.loads(str(item_group).replace("'", '"'), object_hook=decode_inventory_item_group))
        return Inventory(inventory_item_groups)
    return dct


class InventoryEncoder(json.JSONEncoder):

    def default(self, i):
        if isinstance(i, Inventory):
            json_item_groups = []
            for item_group in i.inventory_item_groups:
                json_item_groups.append(fix_up_json_string(json.dumps(item_group, cls=InventoryItemGroupEncoder, ensure_ascii=False)))
            return {"class": 'inventory', "inventory_item_groups": json_item_groups}
        else:
            return super().default(i)
