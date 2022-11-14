import json

from character.talent import Talent, TalentEncoder, decode_talent
from utils.string_utils import fix_up_json_string


class TalentGroup:
    def __init__(self, name, talents):
        self.name = name
        self.talents = []
        for talent in talents:
            if isinstance(talent, Talent):
                self.talents.append(talent)
            else:
                self.add_talent(talent[0], talent[1])

    def add_talent(self, talent_name, talent_value):
        self.talents.append(Talent(self.name, talent_name, talent_value))


def decode_talent_group(dct):
    if dct['class'] == "talent_group":
        talents_in_group = []
        for talent in dct['talents']:
            talents_in_group.append(json.loads(str(talent).replace('%', '"').replace("'", '"'), object_hook=decode_talent))
        return TalentGroup(dct['name'], talents_in_group)
    return dct


class TalentGroupEncoder(json.JSONEncoder):

    def default(self, t):
        if isinstance(t, TalentGroup):
            json_talents = []
            for talent in t.talents:
                json_talents.append(fix_up_json_string(json.dumps(talent, cls=TalentEncoder, ensure_ascii=False)))
            return {"class": 'talent_group', "name": t.name, "talents": json_talents}
        else:
            return super().default(t)

