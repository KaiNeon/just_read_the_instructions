# Import
import logging
import json
import os.path

# Settings
CONF_DIR = "test.json"
CODE_DIR = ""
CUR_DIR = os.getcwd()
CONF_TEMPLATE = "conf_"


# Functions
def get_data(file_dir=CONF_DIR):
    with open(file_dir, 'r', encoding='utf8') as file:
        return json.load(file)


def create_config(file_name, data, file_dir):
    with open(file_dir, 'r', encoding='utf8') as file:
        json.dump(file, data)


def mark_groups(array):
    result = ", ".join(array)
    return result


def compare_part_asset(cur_ver_data, new_ver_data, partname, mirror=False):
    cur_ver_part = set(map(lambda x: x.get('name'), cur_ver_data.get(partname)))
    new_ver_part = set(map(lambda x: x.get('name'), new_ver_data.get(partname)))
    if mirror:
        return list(cur_ver_part.difference(new_ver_part))
    else:
        return list(new_ver_part.difference(cur_ver_part))


def compare_versions(cur_ver_data=get_data('test_prev.json'), new_ver_data=get_data('test.json')):
    add_user = (compare_part_asset(cur_ver_data, new_ver_data, 'users'))
    add_group = (compare_part_asset(cur_ver_data, new_ver_data, 'groups'))
    del_user = (compare_part_asset(cur_ver_data, new_ver_data, 'users', True))
    ver_data = {'users': [unit for unit in new_ver_data.get('users') if unit.get('name') in add_user],
                'groups': [unit for unit in new_ver_data.get('groups') if unit.get('name') in add_group]}
    for unit in del_user:
        ver_data['users'].append({'name': unit, 'remove': 'yes'})
    return ver_data


def clear_filename(filename):
    return filename.split('.')[0].replace(CONF_TEMPLATE, '')


def get_current_ver(dir=CUR_DIR, template=CONF_TEMPLATE):
    file_list = [clear_filename(file) for file in os.listdir(dir) if CONF_TEMPLATE in file]
    file_list = [int(file) for file in file_list if file.isdigit()]
    ver = 0
    if file_list:
        ver = max(file_list)
    return ver


def create_add_task(data=compare_versions(), version=get_current_ver() + 1):
    # names matching
    parts_match = {'users': 'user', 'groups': 'group'}
    action_dict = {'create': 'Creating', 'remove': 'Removing'}
    # strings
    module = '- '
    spaces = '  '

    file = open(CONF_TEMPLATE + str(version) + '.yml', 'w')
    file.write("---\n# Version: " + str(version) + "\ntasks:\n")
    for part in data.keys():
        for unit in data[part]:
            if 'remove' in unit.keys():
                action = action_dict['remove']
            else:
                action = action_dict['create']
            file.write(module + f"name: {action} {parts_match[part]} <{unit.get('name')}>\n")
            file.write(spaces + parts_match[part] + ':\n')
            for line in unit.keys():
                if type(unit.get(line)) == list:
                    if unit.get(line):
                        file.write(spaces*2 + line + ': ' + ', '.join(unit.get(line)) + '\n')
                else:
                    file.write(spaces*2 + line + ': ' + unit.get(line) + '\n')
    file.close()
    return False


# print(create_task())
# print(get_current_ver())

create_add_task()

# result = [data_users, data_groups]
# return result
# xui
# Main
# print(parse())
