import os
import sys

from utils.constants import BASE_PATH, SRC_PATH

os.chdir(SRC_PATH)

sys.path.append(str(BASE_PATH / 'tests' / 'mocks'))
sys.path.insert(0, '.')

import tests.mocks._patches  # noqa - extend existing python modules
