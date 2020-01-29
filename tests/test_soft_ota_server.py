import os
import subprocess
from unittest import TestCase

from utils.constants import BASE_PATH


class SoftOtaServerTestCase(TestCase):
    def test_make_soft_ota(self):
        env = os.environ.copy()
        env['OTA_NO_LOOP'] = 'yes'
        output = subprocess.check_output(
            ['make soft-ota'],
            env=env,
            cwd=str(BASE_PATH),
            shell=True,
            universal_newlines=True
        )
        print(output)

        assert 'Lint code with flake8' in output
        assert 'flake8, ok.' in output

        assert 'Compile via mpy_cross' in output
        assert '+ src/webswitch.py -> bdist/webswitch.mpy' in output

        assert 'Copy files...' in output
        assert '+ src/boot.py -> bdist/boot.py' in output

        assert 'Start OTA Server' in output
        assert 'Wait vor devices on port: 8267' in output
        assert 'Exit after one try, because OTA_NO_LOOP is set, ok.' in output
        assert 'Update 0 device(s), ok.' in output
