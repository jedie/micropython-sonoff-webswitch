import shutil
import sys
from pathlib import Path

import mpy_cross

# mpy_cross.run('--help')


def compile(src_path, dst_path, skip_files):
    cwd = Path().cwd()

    print('Compile files from:', src_path)
    for file_path in sorted(src_path.glob('*.py')):
        file_path = file_path.relative_to(cwd)

        if file_path.name in skip_files:
            continue

        output_path = Path(dst_path, file_path.name).with_suffix('.mpy')
        output_path = output_path.relative_to(cwd)

        print(f' + {file_path} -> {output_path}')
        mpy_cross.run(
            '-O999',  # https://gitlab.com/alelec/mpy_cross/issues/5
            '-v',
            '-v',
            '-v',
            str(file_path),
            '-o', str(output_path)
        )


def create_bdist(src_path, dst_path, copy_files, copy_file_pattern):
    src_path = src_path.resolve()
    dst_path = dst_path.resolve()
    dst_path.mkdir(exist_ok=True)
    compile(
        src_path=src_path,
        dst_path=dst_path,
        skip_files=copy_files
    )
    print(' -' * 50)
    print('Copy files...')
    cwd = Path().cwd()
    files2copy = set([Path(src_path, n) for n in copy_files])
    for pattern in copy_file_pattern:
        files2copy.update(set(src_path.glob(pattern)))

    for file_path in files2copy:
        file_path = file_path.resolve().relative_to(cwd)
        output_path = Path(dst_path, file_path.name).relative_to(cwd)
        print(f' + {file_path} -> {output_path}')
        try:
            shutil.copyfile(file_path, output_path)
        except FileNotFoundError as e:
            print(f'ERROR: {e}', file=sys.stderr)
