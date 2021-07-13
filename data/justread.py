# Import
import os.path
import time
import sys
import json
import logging
import argparse


# Parser
def create_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument('-i', '--input', default=os.path.join(os.getcwd(), "test.json"))
    parser.add_argument('-o', '--output', default="config.yml")
    return parser


# Settings
CurrentDir = os.getcwd()
KeysDir = os.path.join(os.getcwd(), 'keys')


# Functions
def get_data(filepath):
    try:
        with open(filepath, 'r', encoding='utf8') as file:
            return json.load(file)
    except:
        logging.error(f"No such file or directory {filepath}")
        time.sleep(0.5)
        data = {'users': [], 'groups': []}
        return data


def get_keys(data, directory):
    users_with_keys = []
    for user in data['users']:
        if user.name in os.listdir(directory):
            users_with_keys.append(user.name)
    return users_with_keys


def gen_key_auth(unit):
    task_str = ""
    module = '- '
    spaces = '  '
    task_str += (module + f"name: Adding key for <{unit.get('name')}>\n")
    task_str += (spaces + "authorized_key:\n")
    task_str += (spaces * 2 + f"user: {unit.get('name')}\n")
    task_str += (spaces * 2 + "key:" + f"/home/{unit.get('name')}/.ssh/id_rsa.pub\n")
    task_str += (spaces * 2 + "state: present\n")
    return task


def create_add_task(data=None, output_filename=None):
    # Keys translation (dicts)
    parts_match = {'users': 'user', 'groups': 'group', 'keys': 'key'}
    action_dict = {'add': 'Adding', 'remove': 'Removing'}

    # Format-easy strings
    module = '- '
    spaces = '  '

    # Check if data is empty
    if not data.items():
        logging.error("Data empty!")
        exit(-1)

    # Writing task to .yml file
    file = open(os.path.join(CurrentDir, output_filename), 'w')
    file.write("---\ntasks:\n")
    # Check who have keys
    users_with_keys = get_keys(data, KeysDir)

    for part in data.keys():
        for unit in data[part]:
            file.write('\n')
            # Action choose
            if 'remove' in unit.keys():
                action = action_dict['remove']
            else:
                action = action_dict['add']
            # Add/Remove task
            file.write(module + f"name: {action} {parts_match[part]} <{unit.get('name')}>\n")
            file.write(spaces + parts_match[part] + ':\n')
            for line in unit.keys():
                if type(unit.get(line)) == list:
                    if unit.get(line):
                        file.write(spaces * 2 + line + ': ' + ', '.join(unit.get(line)) + '\n')
                else:
                    file.write(spaces * 2 + line + ': ' + unit.get(line) + '\n')
            # Adding key if key exist
            if unit.name in users_with_keys and action != action_dict['remove'] and part != 'groups':
                file.write(gen_key_auth(unit))
            if


    file.close()
    return False


# Init
if __name__ == '__main__':
    parser = create_parser()
    arg = parser.parse_args(sys.argv[1:])
    create_add_task(get_data(arg.input), arg.output)
