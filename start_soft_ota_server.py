#!/usr/bin/env python3

from soft_ota.ota_server import SoftOtaServer
from utils.main import lint_and_compile

PORT = 8267

if __name__ == '__main__':

    lint_and_compile()

    print('_' * 100)
    print('Start OTA Server\n')

    ota_server = SoftOtaServer(verbose=False)

    # Send 'bdist' files to devices:
    clients = ota_server.run(port=PORT)

    print('_' * 100)
    print(f'Update {len(clients)} device(s), ok.')
