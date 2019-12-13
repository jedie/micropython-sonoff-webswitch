import os
import shutil
import sys
import tempfile
from pathlib import Path


class IsolatedFilesystem:
    def __init__(self, prefix=None, add_to_sys_path=False):
        self.prefix = prefix
        self.add_to_sys_path = add_to_sys_path
        self.cwd = None

    def __enter__(self):
        self.cwd = Path().cwd()
        self.temp_path = tempfile.mkdtemp(prefix=self.prefix)
        os.chdir(self.temp_path)

        if self.add_to_sys_path:
            Path(self.temp_path, '__init__.py').touch()
            sys.path.append(str(self.temp_path))
        #     sys.path.insert(0, str(self.temp_path))

    def __exit__(self, exc_type, exc_val, exc_tb):
        os.chdir(self.cwd)
        try:
            shutil.rmtree(self.temp_path)
        except (OSError, IOError):
            pass

        if self.add_to_sys_path:
            sys.path = sys.path[:-1]
