import time
from pathlib import Path

from ota.compile import create_bdist
from ota.ota_server import OtaServer

PORT = 8266

if __name__ == '__main__':
    src_path = Path('src')
    bdist_path = Path('bdist')

    ota_server = OtaServer(
        src_path=bdist_path,  # Put these files on micropython device
        verbose=False,
    )

    while True:

        # Compile via mpy_cross
        create_bdist(
            src_path=src_path,
            dst_path=bdist_path,
            copy_files=(
                # Theses files will be not compiled.
                # They are just copied from src to bdist.
                'boot.py', 'main.py',
                'delete_py_files.py',
            ),
            copy_file_pattern=(
                # Copy all these files from src to bdist:
                '*.html', '*.css', '*.js'
            )
        )

        # Send 'bdist' files to devices:
        clients = ota_server.run(port=PORT)

        print('_' * 100)
        print(f'Update {len(clients)} device(s), ok.')
        time.sleep(2)
