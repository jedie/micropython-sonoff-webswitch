from mpy_tests.test_device_name import run_all_device_name_tests
from mpy_tests.test_power_timer import run_all_power_timer_tests
from mpy_tests.test_times_utils import run_all_times_utils_tests
from mpy_tests.test_timezone import run_all_timezone_tests
from tests.base import MicropythonBaseTestCase
from tests.utils.mock_py_config import mock_py_config_context


class MPyTestCase(MicropythonBaseTestCase):
    def test_timezone(self):
        with mock_py_config_context():
            run_all_timezone_tests()

    def test_power_timer(self):
        with mock_py_config_context():
            run_all_power_timer_tests()

    def test_device_name(self):
        with mock_py_config_context():
            run_all_device_name_tests()

    def test_times_utils(self):
        with mock_py_config_context():
            run_all_times_utils_tests()
