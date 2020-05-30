import json


def remove_extension(path: str):
    parts = path.split('.')
    return '.'.join(parts[:-1])


def load_json(path: str):
    with open(path, 'r') as f:
        return json.load(f)


def check_extension(file_name, exts):
    if not file_name.endswith(exts):
        raise ValueError('only ' + str(exts) + ' are accepted for grading')
