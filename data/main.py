# Import
import logging
import json
import os.path

# Settings
CUR_DIR = os.getcwd()
CONF_TEMP = "conf_"
STORE_TEMP = "stored_"
STORED_TEMP = CONF_TEMP + STORE_TEMP
STORE_DIR = os.path.join(os.path.abspath(os.path.join(CUR_DIR, os.pardir)), 'store')
NEW_CONFIG_FILE = "test.json"
NEW_CONFIG_PATH = os.path.join(CUR_DIR, NEW_CONFIG_FILE)


# Functions
def clear_filename(filename):
    return filename.split('.')[0].replace(STORED_TEMP, '')


def get_current_ver(template=CONF_TEMP + STORE_TEMP):
    file_list = [clear_filename(file) for file in os.listdir(STORE_DIR) if CONF_TEMP in file]
    file_list = [int(file) for file in file_list if file.isdigit()]
    ver = 0
    if file_list:
        ver = max(file_list)
    return ver


def get_config_log_path(blink=0, filename=None, filedir=None):
    if not filename:
        filename = CONF_TEMP + STORE_TEMP + str(get_current_ver() + blink) + '.json'
    if not filedir:
        filedir = STORE_DIR
    filepath = os.path.join(filedir, filename)
    return filepath


def get_data(file_path):
    with open(file_path, 'r', encoding='utf8') as file:
        return json.load(file)


def create_config_log(data, filepath=None):
    if not filepath:
        filepath = get_config_log_path()
    with open(filepath, 'w', encoding='utf8') as file:
        json.dump(data, file, indent=2)


def compare_part_asset(cur_ver_data, new_ver_data, partname, mirror=False):
    # Creating sets to comparing easly
    cur_ver_part = set(map(lambda x: x.get('name'), cur_ver_data.get(partname)))
    new_ver_part = set(map(lambda x: x.get('name'), new_ver_data.get(partname)))

    # Creating lists from sets difference to Create/Remove units
    if mirror:
        return list(cur_ver_part.difference(new_ver_part))
    else:
        return list(new_ver_part.difference(cur_ver_part))


def compare_versions(cur_ver_path=None, new_ver_path=None):
    # Data collecting
    if not cur_ver_path:
        cur_ver_path = get_config_log_path(1)
    cur_ver_data = get_data(cur_ver_path)
    if not new_ver_path:
        new_ver_path = NEW_CONFIG_PATH
    new_ver_data = get_data(new_ver_path)

    # Comparing
    add_user = (compare_part_asset(cur_ver_data, new_ver_data, 'users'))
    add_group = (compare_part_asset(cur_ver_data, new_ver_data, 'groups'))
    del_user = (compare_part_asset(cur_ver_data, new_ver_data, 'users', True))
    ver_data = {'users': [unit for unit in new_ver_data.get('users') if unit.get('name') in add_user],
                'groups': [unit for unit in new_ver_data.get('groups') if unit.get('name') in add_group]}

    # Creating configuration log
    create_config_log(new_ver_data)

    # Updating task data with objects to remove
    for unit in del_user:
        ver_data['users'].append({'name': unit, 'remove': 'yes'})
    return ver_data


def create_add_task(data=None):
    # Data collecting
    if not data:
        data = compare_versions()

    # Keys translation (dicts)
    parts_match = {'users': 'user', 'groups': 'group'}
    action_dict = {'create': 'Creating', 'remove': 'Removing'}

    # Format-easy strings
    module = '- '
    spaces = '  '

    # Check if data is empty
    if not data.items():
        logging.warning("Nothing changed!")
        return True

    # Writing task to .yml file
    file = open(CONF_TEMP + str(get_current_ver()) + '.yml', 'w')
    file.write("---\n# Version: " + str(get_current_ver()) + "\ntasks:\n")
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
                        file.write(spaces * 2 + line + ': ' + ', '.join(unit.get(line)) + '\n')
                else:
                    file.write(spaces * 2 + line + ': ' + unit.get(line) + '\n')
    file.close()
    return False


# Init
create_add_task()
