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


def mark_groups(array):
    result = ", ".join(array)
    return result


def compare_part(cur_ver_data, new_ver_data, partname, mirror=False):
    cur_ver_part = set(map(lambda x: x.get('name'), cur_ver_data.get(partname)))
    new_ver_part = set(map(lambda x: x.get('name'), new_ver_data.get(partname)))
    if mirror:
        return cur_ver_part.difference(new_ver_part)
    return new_ver_part.difference(cur_ver_part)


def compare_versions(cur_ver_data=get_data('test_prev.json'), new_ver_data=get_data('test.json')):
    print(compare_part(cur_ver_data, new_ver_data, 'users'))
    print(compare_part(cur_ver_data, new_ver_data, 'groups'))
    print(compare_part(cur_ver_data, new_ver_data, 'users', True))
    print(compare_part(cur_ver_data, new_ver_data, 'groups', True))
    pass


def clear_filename(filename):
    return filename.split('.')[0].replace(CONF_TEMPLATE, '')


def get_current_ver(dir=CUR_DIR, template=CONF_TEMPLATE):
    file_list = [clear_filename(file) for file in os.listdir(dir) if CONF_TEMPLATE in file]
    file_list = [int(file) for file in file_list if file.isdigit()]
    ver = 0
    if file_list:
        ver = max(file_list)
    return ver


def create_add_task(data=get_data(), version=get_current_ver() + 1):
    file = open(CONF_TEMPLATE + str(version), 'w')
    users = data.get('users')
    groups = data.get('groups')
    task = "---"
    task += "\n# Version: " + str(version)
    task += "\ntasks:"
    for unit in users:
        task += f"""
- name: Creating user <{unit.get('name')}>
  user:
    name: {unit.get('name')}
    password: {unit.get('password')}
    groups: {", ".join(unit.get('groups'))}
        """
    for unit in groups:
        task += f"""
- name: Creating group <{unit.get('name')}>
  group:
    name: {unit.get('name')}
        """
    return task


def create_del_task():
    pass


def create_task_file():
    pass


# print(create_task())
# print(get_current_ver())

compare_versions()

# result = [data_users, data_groups]
# return result
# xui
# Main
# print(parse())
