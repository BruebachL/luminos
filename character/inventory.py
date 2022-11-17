import json

from character.inventory_item_group import decode_inventory_item_group, InventoryItemGroupEncoder
from utils.string_utils import fix_up_json_string


class Inventory:

    def __init__(self, inventory_item_groups=None):
        if inventory_item_groups is None:
            inventory_item_groups = []
        self.inventory_item_groups = inventory_item_groups

def decode_inventory(dct):
    if dct['class'] == "inventory":
        inventory_item_groups = []
        for item_group in dct['inventory_item_groups']:
            print(item_group)
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
