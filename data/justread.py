# Import
import os.path
import sys
import json
import logging
import argparse


# Parser
def create_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument('-i', '--input', default=os.path.join(os.getcwd(), "test.json"))
    parser.add_argument('-o', '--output', default=os.path.join(os.getcwd(), "config.yml"))
    return parser


# Settings
CurrentDir = os.getcwd()
KeysDir = os.path.join(os.getcwd(), 'keys')

# Preset
Tabs = {
    'spaces': '  ',
    'spacesX2': '  ' * 2,
    'module': '- '
}
Action_dict = {
    'add': 'Adding',
    'remove': 'Removing'
}


# Functions
def get_data(filepath):
    try:
        with open(filepath, 'r', encoding='utf8') as file:
            return json.load(file)
    except:
        logging.error(f"No such file or directory {filepath}")
        data = {'users': [], 'groups': []}
        return data


def check_key(username, directory=KeysDir):
    if username in os.listdir(directory):
        return True
    return False


def task_syntax_string(action, module, additional=''):
    if not type(additional) == dict:
        additional = {'name': str(additional)}
    additional = additional.get('name')
    syntax_string = f"{Tabs.get('module')}name: {action} {module} {additional}\n"
    syntax_string += f"{Tabs.get('spaces')}{module}:\n"
    return syntax_string


def subject_syntax_string(unit):
    syntax_string = ""
    for line in unit.keys():
        if type(unit.get(line)) == list:
            if unit.get(line):
                syntax_string += f"{Tabs.get('spacesX2')}{line}: {', '.join(unit.get(line))}\n"
        else:
            syntax_string += f"{Tabs.get('spacesX2')}{line}: {unit.get(line)}\n"
    syntax_string += f"{Tabs.get('spacesX2')}state: present\n"
    return syntax_string


def authkey_syntax_string(unit):
    syntax_string = "\n"
    syntax_string += f"{Tabs.get('module')}name: Setting key for {unit.get('name')}\n"
    syntax_string += f"{Tabs.get('spaces')}authorized_key:\n"
    syntax_string += f"{Tabs.get('spacesX2')}user: {unit.get('name')}\n"
    syntax_string += f"{Tabs.get('spacesX2')}key: {os.path.join(KeysDir, unit.get('name'))}\n"
    syntax_string += f"{Tabs.get('spacesX2')}state: present\n"
    return syntax_string


def generate_task(action, module, unit):
    task_string = ""
    if module == 'user':
        task_string += task_syntax_string(action, module, unit)
        task_string += subject_syntax_string(unit)
        if check_key(unit.get('name')):
            task_string += authkey_syntax_string(unit)
    elif module == 'group':
        task_string += task_syntax_string(action, module, unit)
        task_string += subject_syntax_string(unit)
        # - Create sudoers setting
    return task_string


def create_add_task(data, output_path):
    # Writing task to .yml file
    task = ""
    # file = open(os.path.join(output_path), 'w')
    # file.write("---\ntasks:\n")
    for module in data.keys():
        for unit in data[module]:
            task += ('\n')
            # Action syntax choose
            if 'remove' in unit.keys():
                action = Action_dict['remove']
            else:
                action = Action_dict['add']
            # Task generation
            print(action, module, unit)
            task += (generate_task(action, module, unit))

    print(task)
    # file.close()
    return False


# Init
if __name__ == '__main__':
    parser = create_parser()
    arg = parser.parse_args(sys.argv[1:])
    create_add_task(get_data(arg.input), arg.output)
