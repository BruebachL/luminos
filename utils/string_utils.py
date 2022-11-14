def fix_up_json_string(json_string_to_fix):
    return json_string_to_fix.replace('\\"', '"').replace('\\n', '\n').replace('}\"', '}').replace('\"{', '{')