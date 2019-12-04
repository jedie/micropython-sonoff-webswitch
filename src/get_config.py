import ujson as json


def get_config(key=None):
    with open('config.json', 'r') as f:
        if key is None:
            return json.load(f)
        else:
            return json.load(f)[key]
