import json


def remove_extension(path: str):
    parts = path.split('.')
    return '.'.join(parts[:-1])


def load_json(path: str):
    with open(path, 'r') as f:
        return json.load(f)
