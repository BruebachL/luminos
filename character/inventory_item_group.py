import json

from character.inventory_item import InventoryItemEncoder, decode_inventory_item
from utils.string_utils import fix_up_json_string


class InventoryItemGroup(object):

    def __init__(self, name, items=None):
        self.name = name
        if items is None:
            items = []
        self.items = items

def decode_inventory_item_group(dct):
    if dct['class'] == "inventory_item_group":
        items_in_group = []
        for item in dct['items']:
            items_in_group.append(json.loads(str(item).replace('%', '"').replace("'", '"'), object_hook=decode_inventory_item))
        return InventoryItemGroup(dct['name'], items_in_group)
    return dct


class InventoryItemGroupEncoder(json.JSONEncoder):

    def default(self, i):
        if isinstance(i, InventoryItemGroup):
            json_items = []
            for item in i.items:
                json_items.append(fix_up_json_string(json.dumps(item, cls=InventoryItemEncoder, separators=(',', ': '), indent=12, ensure_ascii=False)))
            return {"class": 'inventory_item_group', "name": i.name, "items": json_items}
        else:
            return super().default(i)

