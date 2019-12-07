"""
    Delete all *.py files except 'boot.py' and 'main.py'
    Useful after REPL experiments.
    Start OTA Update to get all needed files back ;)
"""
import uos as os

if __name__ == '__main__':
    for file_name in os.listdir():
        if file_name in ('boot.py', 'main.py'):
            continue
        elif file_name.rsplit('.', 1)[-1] != 'py':
            continue

        print('delete:', file_name)
        os.remove(file_name)

    print('all .py files deleted')
