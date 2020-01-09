from unittest import TestCase


class TestIniSetupTestCase(TestCase):
    def test_boot_py_content(self):
        with open('boot.py', 'r') as f:
            boot_py_content = f.read()

        with open('inisetup.py', 'r') as f:
            inisetup_py_content = f.read()

        assert boot_py_content in inisetup_py_content, (
            'boot.py code in inisetup.py is not up-to-date'
        )
