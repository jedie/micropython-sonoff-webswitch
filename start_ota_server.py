#!/usr/bin/env python3
from pathlib import Path

from ota.ota_server import OtaServer
from utils.main import lint_and_compile

PORT = 8267

if __name__ == '__main__':
    src_path = Path('src')
    bdist_path = Path('bdist')

    lint_and_compile(src_path, bdist_path)

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
