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
    with open(CONF_DIR, 'r', encoding='utf8') as file:
        return json.load(file)


def mark_groups(array):
    result = ", ".join(array)
    return result


def compare_versions(data):
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
    task += "\n# " + str(version)
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

# result = [data_users, data_groups]
# return result
# xui
# Main
# print(parse())
