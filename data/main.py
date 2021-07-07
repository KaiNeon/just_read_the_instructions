# Import
import logging
import json

# Settings
CONF_DIR = "test.json"
CODE_DIR = ""


# Functions
def get_data(file_dir=CONF_DIR):
    with open(CONF_DIR, 'r', encoding='utf8') as file:
        result = json.load(file)
    return result


def mark(data_raw):
    pass
# result = [data_users, data_groups]
# return result

# Main
# print(parse())
