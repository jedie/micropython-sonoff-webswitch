import os
import sys

import pytest
import tests.mocks._patches  # noqa - extend existing python modules
from utils.constants import BASE_PATH, SRC_PATH

sys.path.append(str(BASE_PATH / 'tests' / 'mocks'))
sys.path.insert(0, '.')


@pytest.fixture(autouse=True)
def chdir_src():
    os.chdir(SRC_PATH)
