import json


class Talent:

    def __init__(self, group, name, shorthand, check_against, value):
        self.group = group
        self.name = name
        self.shorthand = shorthand
        self.check_against = check_against
        self.value = value

    def equals(self, talent):
        return self.name == talent.name and self.shorthand == talent.shorthand \
            and self.check_against == talent.check_against and self.value == talent.value


def decode_talent(dct):
    if dct['class'] == "talent":
        return Talent(dct['group'], dct['name'], dct['shorthand'], dct['check_against'], dct['value'])
    return dct


class TalentEncoder(json.JSONEncoder):

    def default(self, t):
        if isinstance(t, Talent):
            return {"class": 'talent', "group": t.group, "name": t.name, "shorthand": t.shorthand, "check_against":
                    t.check_against, "value": t.value}
        else:
            return super().default(t)
