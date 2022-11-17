def fix_up_json_string(json_string_to_fix):
    return json_string_to_fix.replace('\\"', '"').replace('\\n', '\n').replace('}\"', '}').replace('\"{', '{')

def get_free_name(dict, base_name):
    name_found = False
    name_counter = 1
    name = base_name
    while not name_found:
        if name in list(dict):
            name = ' '.join((base_name, str(name_counter)))
            name_counter = name_counter + 1
        else:
            name_found = True