

from mpy_tests.test_power_timer import test_power_timer
from mpy_tests.test_timezone import run_all_timezone_tests
from tests.base import MicropythonBaseTestCase
from tests.utils.mock_py_config import mock_py_config_context


class MPyTestCase(MicropythonBaseTestCase):
    def test_call_run_all_timezone_tests(self):
        with mock_py_config_context():
            run_all_timezone_tests()

    def test_call_test_power_timer(self):
        with mock_py_config_context():
            test_power_timer()
