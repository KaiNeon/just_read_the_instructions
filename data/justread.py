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


def task_syntax_string(action='', module='', additional=''):
    syntax_string = f"\n{Tabs.get('module')}name: {action} {module} {additional}\n"
    syntax_string += f"{Tabs.get('spaces')}{module}:\n"
    return syntax_string


def subject_syntax_string(action, module, unit):
    syntax_string = task_syntax_string(action, module, f"<{unit.get('name')}>")
    for line in unit.keys():
        if type(unit.get(line)) == list:
            if unit.get(line):
                syntax_string += f"{Tabs.get('spacesX2')}{line}: {', '.join(unit.get(line))}\n"
        else:
            syntax_string += f"{Tabs.get('spacesX2')}{line}: {unit.get(line)}\n"
    # syntax_string += f"{Tabs.get('spacesX2')}state: present\n"
    return syntax_string


def authkey_syntax_string(unitname):
    syntax_string = task_syntax_string('Setting', 'authorized_key', f"for <{unitname}>")
    syntax_string += f"{Tabs.get('spacesX2')}user: {unitname}\n"
    syntax_string += f"{Tabs.get('spacesX2')}key: {os.path.join(KeysDir, unitname)}\n"
    syntax_string += f"{Tabs.get('spacesX2')}state: present\n"
    return syntax_string


def sudoers_syntax_string(unitname):
    syntax_string = task_syntax_string('Copying', 'copy', f"sudoers file for group {unitname}")
    return syntax_string


def generate_task(action, module, unit):
    task_string = ""
    rep_unit_name = unit.get('name')
    if module == 'user':
        task_string += subject_syntax_string(action, module, unit)
        if check_key(rep_unit_name):
            task_string += authkey_syntax_string(rep_unit_name)
    elif module == 'group':
        task_string += subject_syntax_string(action, module, unit)
        if check_key(rep_unit_name):
            task_string += subject_syntax_string(action, module, rep_unit_name)
        # - Create sudoers setting
    return task_string


def create_add_task(data, output_path):
    # Writing task to .yml file
    task = ""
    # file = open(os.path.join(output_path), 'w')
    # file.write("---\ntasks:\n")
    for module in data.keys():
        for unit in data[module]:
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
