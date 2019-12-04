import machine
import esp

import uos as os

for file_name in os.listdir():
    if file_name in ('boot.py', 'main.py'):
        continue
    elif file_name.rsplit('.',1)[-1] != 'py':
        continue

    print('delete:', file_name)
    os.remove(file_name)

print('all .py files deleted')
