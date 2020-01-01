from utils.call_flake8 import call_flake8
from utils.compile import create_bdist


def lint_and_compile():
    print('_' * 100)
    print('Lint code with flake8\n')

    call_flake8()

    print('_' * 100)
    print('Compile via mpy_cross\n')

    create_bdist(
        ignore_files=('__init__.py', 'inisetup.py'),
        copy_files=(
            # Theses files will be not compiled.
            # They are just copied from src to bdist.
            'boot.py', 'main.py',
        ),
        copy_file_pattern=(
            # Copy all these files from src to bdist:
            '*.html', '*.css', '*.js', '*.ico'
        )
    )
