#!/usr/bin/env python3

"""
    Generate ./sdist/ with all to freeze modules
    with ./sdist/frozen_modules_info.py that contains
    information of all own freezes modules.

    This can be used for "soft" OTA updates.
"""

import hashlib
import pprint
import shutil
from pathlib import Path

BASE_PATH = Path(__file__).parent.parent  # .../micropython-sonoff-webswitch/

SKIP_FILES = ('__init__.py', 'main.py')

FROZEN_INFO_NAME = 'frozen_modules_info.py'
FROZEN_INFO_TEMPLATE = f"""# This file in generated via .../{Path(__file__).relative_to(BASE_PATH.parent)}
FROZEN_FILE_INFO = {{frozen_info}}
"""


def copy_src_py_files(src_path, sdist_path):
    print('Copy .../src/*.py -> .../sdist/ without SKIP_FILES:\n')
    for file_path in src_path.glob('*.py'):
        if file_path.name in SKIP_FILES:
            print(f' *** Skip: {file_path}')
            continue

        dst_path = Path(sdist_path, file_path.name)
        print(
            f'\t{file_path.relative_to(BASE_PATH)} -> {dst_path.relative_to(BASE_PATH)}'
        )
        shutil.copy(file_path, dst_path)


def generate_frozen_info(sdist_path):
    frozen_info_path = Path(sdist_path, FROZEN_INFO_NAME)
    print(f'\nGenerate {frozen_info_path.relative_to(BASE_PATH)}...', end='', flush=True)

    frozen_info = []
    for file_path in sdist_path.glob('*.py'):
        with file_path.open('rb') as f:
            sha256 = hashlib.sha256(f.read()).hexdigest()

        frozen_info.append(
            (file_path.name, file_path.stat().st_size, sha256)
        )

    with frozen_info_path.open('w') as f:
        f.write(
            FROZEN_INFO_TEMPLATE.format(frozen_info=pprint.pformat(tuple(frozen_info), width=120))
        )

    print('OK')


def main(src_path, sdist_path):
    if sdist_path.is_dir():
        shutil.rmtree(sdist_path)
    sdist_path.mkdir()

    copy_src_py_files(src_path, sdist_path)
    generate_frozen_info(sdist_path)


if __name__ == '__main__':
    main(
        src_path=Path(BASE_PATH, 'src'),
        sdist_path=Path(BASE_PATH, 'sdist')
    )

    # 	mkdir -p sdist
# 	cp -u src/*.py sdist/
#
# 	rm sdist/__init__.py
# 	rm sdist/boot.py
# 	rm sdist/main.py
