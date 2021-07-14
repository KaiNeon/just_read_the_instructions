# Import
import logging
import json
import os.path
import argparse

# Settings
import sys
import time

CUR_DIR = os.getcwd()
CONF_DIR = CUR_DIR
STORE_DIR = os.path.join(os.path.abspath(os.path.join(CUR_DIR, os.pardir)), 'store')
CONF_TEMP = "conf_"
STORE_TEMP = "stored_"
STORED_TEMP = CONF_TEMP + STORE_TEMP


# Parser
def create_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument('-s', '--store', default=STORE_DIR)
    parser.add_argument('-i', '--input')
    parser.add_argument('-o', '--output', default=CONF_DIR)
    return parser


# Functions
def clear_filename(filename):
    return filename.split('.')[0].replace(STORED_TEMP, '')


def get_current_ver(template=CONF_TEMP + STORE_TEMP):
    file_list = [clear_filename(file) for file in os.listdir(STORE_DIR) if CONF_TEMP in file]
    file_list = [int(file) for file in file_list if file.isdigit()]
    ver = 0
    if file_list:
        ver = max(file_list)
    else:
        logging.warning(f"Cannot find current version in {STORE_DIR}")
    return ver


def get_config_log_path(blink=0, filename=None, filedir=None):
    if not filename:
        filename = CONF_TEMP + STORE_TEMP + str(get_current_ver() + blink) + '.json'
    if not filedir:
        filedir = STORE_DIR
    filepath = os.path.join(filedir, filename)
    return filepath


def create_config_log(data, filepath=None):
    if not filepath:
        filepath = get_config_log_path(1)
    with open(filepath, 'w', encoding='utf8') as file:
        json.dump(data, file, indent=2)


def get_data(filepath):
    try:
        with open(filepath, 'r', encoding='utf8') as file:
            return json.load(file)
    except:
        logging.error(f"No such file or directory {filepath}")
        time.sleep(0.5)
        if input("Should I create empty file as current version? [y if yes]") == 'y':
            data = {'users': [], 'groups': []}
            create_config_log(data, filepath)
            return data
        else:
            exit(-1)


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
        cur_ver_path = get_config_log_path()
    cur_ver_data = get_data(cur_ver_path)
    if not new_ver_path:
        logging.warning(f"No data in (new version path) {new_ver_path}")
        time.sleep(0.5)
        if input("Should I use 'test.json' as new version datafile? [y if yes]") == 'y':
            new_ver_path = os.path.join(CUR_DIR, 'test.json')
        else:
            exit(-1)
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


def create_add_task(data=None, output_dir=None):
    # Data collecting
    if not data:
        data = compare_versions()
    if not output_dir:
        output_dir = CUR_DIR

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
    output_filename = CONF_TEMP + str(get_current_ver()) + '.yml'
    file = open(os.path.join(output_dir, output_filename), 'w')
    file.write("---\n# Version: " + str(get_current_ver()) + "\ntasks:\n")
    for part in data.keys():
        for unit in data[part]:
            file.write('\n')
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


# Checking settings.json
settings = get_data(os.path.join(CUR_DIR, 'settings.json'))
if settings['store_dir']:
    STORE_DIR = settings['store_dir']
if settings['config_dir']:
    CONF_DIR = settings['config_dir']
if settings['config_template']:
    CONF_TEMP = settings['config_template']
if settings['stored_template']:
    STORED_TEMP = settings['stored_template']

# Init
if __name__ == '__main__':
    parser = create_parser()
    namespace = parser.parse_args(sys.argv[1:])
    STORE_DIR = namespace.store
    create_add_task(compare_versions(get_config_log_path(), namespace.input), namespace.output)

# create_add_task()
