import importlib
import sys
import traceback
from contextlib import contextmanager
from pathlib import Path
from unittest import mock

from tests.utils.isolates_filesystem import IsolatedFilesystem


class NonCachesImporter:
    """
    replace __import__() with a non-cached import

    https://docs.python.org/3/library/importlib.html#importing-a-source-file-directly
    """

    def __init__(self):
        self.origin_import = __import__

    def mocked_import(self, module_name, *args, **kwargs):
        if args != (None, None):
            # print(f'\nReal import: {module_name!r}')
            return self.origin_import(module_name, **kwargs)

        print(f'\nMocked import: {module_name!r}')
        # print(f'Mocked import: {module_name!r} with {args!r} {kwargs!r}')

        file_path = Path(f'{module_name}.py').resolve()
        if not file_path.is_file():
            # convert a FileNotFoundError into normal ImportError
            msg = f'File not found: {file_path.name}'
            print(msg)
            raise ImportError(msg)
        else:
            print('Existing file:', file_path)

        with file_path.open('r') as f:
            print('Content:', repr(f.read()))

        spec = importlib.util.spec_from_file_location(module_name, file_path)
        module = importlib.util.module_from_spec(spec)
        sys.modules[module_name] = module
        spec.loader.exec_module(module)

        # module = importlib.reload(module) # will fail!

        print('imported:', module, id(module))
        print('%s.value: %r' % (module_name, getattr(module, 'value', '-')))

        return module

    def __call__(self, *args, **kwargs):
        try:
            return self.mocked_import(*args, **kwargs)
        except ImportError:
            raise
        except BaseException as e:
            traceback.print_exception(None, e, sys.exc_info()[2])
            raise RuntimeError(e)


@contextmanager
def mock_py_config_context():
    with IsolatedFilesystem():
        with mock.patch('builtins.__import__', NonCachesImporter()):
            yield
