import logging
import sys
from pathlib import Path

from flake8.main import cli as flake8cli

from ota.compile import create_bdist
from ota.ota_server import OtaServer

PORT = 8266


def call_flake8():
    log = logging.getLogger('flake8')
    log.setLevel(logging.INFO)
    log.addHandler(logging.StreamHandler(stream=sys.stdout))

    logging.getLogger('flake8.plugins.manager').setLevel(logging.WARNING)

    try:
        flake8cli.main(argv=['.'])
    except SystemExit as e:
        if e.code is False:
            print('flake8, ok.')
            return
        raise


if __name__ == '__main__':
    src_path = Path('src')
    bdist_path = Path('bdist')

    print('_' * 100)
    print('Lint code with flake8\n')

    call_flake8()

    print('_' * 100)
    print('Compile via mpy_cross\n')

    create_bdist(
        src_path=src_path,
        dst_path=bdist_path,
        copy_files=(
            # Theses files will be not compiled.
            # They are just copied from src to bdist.
            'boot.py', 'main.py',
        ),
        copy_file_pattern=(
            # Copy all these files from src to bdist:
            '*.html', '*.css', '*.js'
        )
    )

    print('_' * 100)
    print('Start OTA Server\n')

    ota_server = OtaServer(
        src_path=bdist_path,  # Put these files on micropython device
        verbose=False,
    )

    # Send 'bdist' files to devices:
    clients = ota_server.run(port=PORT)

    print('_' * 100)
    print(f'Update {len(clients)} device(s), ok.')
