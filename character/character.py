import json

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
    def __init__(self, name, fields):
        self.name = name
        self.talent_groups = []
        self.fields = []
        self.add_talents(fields)

    def add_talents(self, groups):
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


def decode_character(dct):
    if dct['class'] == "character":
        talent_groups = []
        for talent_group in dct['talent_groups']:
            print(talent_group)
            talent_groups.append(json.loads(str(talent_group).replace("'", '"'), object_hook=decode_talent_group))
        return Character(dct['name'], talent_groups)
    return dct


class CharacterEncoder(json.JSONEncoder):

    def default(self, c):
        if isinstance(c, Character):
            json_talents = []
            for talent_group in c.talent_groups:
                json_talents.append(fix_up_json_string(json.dumps(talent_group, cls=TalentGroupEncoder, ensure_ascii=False)))
            return {"class": 'character', "name": c.name, "talent_groups": json_talents}
        else:
            return super().default(c)
