import subprocess
from pathlib import Path

BASE_PATH = Path(__file__).parent.parent  # .../micropython-sonoff-webswitch/

mpy_cross = Path(BASE_PATH, 'build', 'mpy-cross')


def assert_mpy_cross_exists():
    if not mpy_cross.is_file():
        raise FileNotFoundError(f'mpy-cross not found here: {mpy_cross.relative_to(BASE_PATH)}')


def run(*args, **kwargs):
    assert_mpy_cross_exists()
    return subprocess.Popen([mpy_cross] + list(args), **kwargs)


def check_output(*args, universal_newlines=True, **kwargs):
    return subprocess.check_output(
        [mpy_cross] + list(args),
        universal_newlines=universal_newlines,
        **kwargs
    )


def version():
    """
    Returns 'mpy_cross' version as string e.g.:
        'v1.12'
    """
    # official build, e.g.:
    #   'MicroPython v1.12 on 2019-12-21; mpy-cross emitting mpy v5\n'
    #
    # own compilation, e.g.::
    #   'MicroPython 1070984 on 2020-01-01; mpy-cross emitting mpy v5\n'
    raw_mpy_cross_version = check_output('--version').strip()
    print(f'Installed mpy_cross version is for {raw_mpy_cross_version}')
    assert raw_mpy_cross_version.startswith('MicroPython ')
    version = raw_mpy_cross_version.split(' ', 2)[1]
    return version


if __name__ == '__main__':
    print(repr(check_output('--version')))
    print(f'mpy_cross version: {version()!r}')
