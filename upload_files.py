
from pathlib import Path

from utils.main import lint_and_compile
from utils.sync import sync

PORT = 8266


if __name__ == '__main__':
    src_path = Path('src')
    bdist_path = Path('bdist')

    lint_and_compile(src_path, bdist_path)

    print('_' * 100)
    print('Sync bdist files\n')

    sync(
        src_path=bdist_path,
        verbose=True,
    )
