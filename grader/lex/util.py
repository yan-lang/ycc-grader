def remove_extension(path: str):
    parts = path.split('.')
    return '.'.join(parts[:-1])
