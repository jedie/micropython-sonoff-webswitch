import os
import sys

import tests.mocks._patches  # noqa - extend existing python modules
from utils.constants import BASE_PATH, SRC_PATH

sys.path.append(str(BASE_PATH / 'tests' / 'mocks'))

os.chdir(SRC_PATH)
sys.path.insert(0, '.')
