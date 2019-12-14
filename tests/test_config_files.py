from unittest import TestCase

from config_files import restore_py_config, save_py_config
from mpy_tests.test_config_files import test_json_config
from tests.utils.isolates_filesystem import IsolatedFilesystem
from tests.utils.mock_py_config import mock_py_config_context


class JsonConfigTestCase(TestCase):
    def test_json_config(self):
        with IsolatedFilesystem():
            test_json_config()


class PyConfigTestCase(TestCase):
    def test_mock_py_config_context(self):
        with mock_py_config_context():
            # check mock if file not exist, yet:
            with self.assertRaises(ImportError) as cm:
                __import__('not_existing_module', None, None)

            self.assertEqual(
                cm.exception.args[0],
                'File not found: not_existing_module.py')  # Own error?

            # Check mock if file exists:
            with open('test.py', 'w') as f:
                f.write('variable=True')
            test = __import__('test', None, None)
            assert test.variable is True

    def test_py_config(self):
        with mock_py_config_context():

            # test_py_config() # will not work!

            save_py_config(module_name='test_int', value=1)
            assert restore_py_config(module_name='test_int') == 1

            save_py_config(module_name='test_dict', value={'foo': 1.2})
            assert restore_py_config(module_name='test_dict') == {'foo': 1.2}
