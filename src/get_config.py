import json

CONFIG_FILE='config.json'

print('Read %r...' % CONFIG_FILE)

try:
    with open('config.json', 'r') as f:
        config = json.load(f)
except OSError:
    import os
    if not CONFIG_FILE in os.listdir():
        raise OSError('File not found: %r ! Please create&upload it to device!' % CONFIG_FILE)
    raise

print('Existing settings:', config.keys())
print('Known WiFi settings:', config['wifi'].keys())