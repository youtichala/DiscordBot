import json

story = None

def get_json(path):
    global story
    f = open(path, 'r', encoding='utf-8')
    story = json.load(f)
    f.close()


def get_value(key):
    for paragraph in story:
        if paragraph['key'] == key:
            return paragraph['value']
    return None
