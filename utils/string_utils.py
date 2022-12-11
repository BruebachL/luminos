def fix_up_json_string(json_string_to_fix):
    if json_string_to_fix is None or json_string_to_fix == 'null' or json_string_to_fix == 'None': return None
    return json_string_to_fix.replace('\\"', '"').replace('\\n', '\n').replace('}\"', '}').replace('\"{', '{')

def get_free_name(base_name, existing_names):
    name_found = False
    name_counter = 0
    name = base_name
    existing_names_list = list(existing_names)
    while not name_found:
        if name in existing_names_list:
            name_counter = name_counter + 1
            name = ' '.join((base_name, str(name_counter)))
        else:
            name_found = True
    return name