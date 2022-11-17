import json


class InventoryItem(object):

    def __init__(self, group, name=None, description=None, weight=None):
        if name is None:
            name = ""
        if description is None:
            description = ""
        if weight is None:
            weight = 0
        elif isinstance(weight, str):
            weight = float(weight)
        self.group = group
        self.name = name
        self.description = description
        self.weight = weight

    def equals(self, inventory_item):
        return self.group == inventory_item.group and self.name == inventory_item.name \
            and self.description == inventory_item.description and self.weight == inventory_item.weight

def decode_inventory_item(dct):
    if dct['class'] == "inventory_item":
        return InventoryItem(dct['group'], dct['name'], dct['description'], dct['weight'])
    return dct


class InventoryItemEncoder(json.JSONEncoder):

    def default(self, i):
        if isinstance(i, InventoryItem):
            return {"class": 'inventory_item', "group": i.group, "name": i.name, "description": i.description,
                    "weight": i.weight}
        else:
            return super().default(i)
