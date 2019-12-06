import logging
import sys

from flake8.main import cli as flake8cli


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
