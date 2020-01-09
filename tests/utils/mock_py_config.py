import ast
import sys
import traceback
from contextlib import contextmanager
from pathlib import Path
from unittest import mock


class MockedModule:
    pass


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

        # It's very difficult to disable the CPython import caching.
        # What doesn't work is, e.g.:
        #   * `del sys.modules[module_name]` before import
        #   * module = importlib.reload(module)
        #   * Using low-level stuff from `importlib.util`
        #
        # So we parse the content via ast.literal_eval() and create
        # a mocked sys.modules entry

        with file_path.open('r') as f:
            content = f.read()
        print('Content:', repr(content))

        module = MockedModule()
        for line in content.splitlines():
            if line == 'from micropython import const':
                continue

            var_name, data = line.split('=')

            var_name = var_name.strip()
            data = data.strip()

            if 'const(' in data:
                # 'const(123)' -> '123'
                data = data.split('(', 1)[1].rstrip(')')

            data = ast.literal_eval(data)
            setattr(module, var_name, data)
            break  # there is currently one one value

        # Add to sys.modules, so that "del sys.modules[module_name]" will work
        # used in config_files.restore_py_config()
        sys.modules[module_name] = module

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
    with mock.patch('builtins.__import__', NonCachesImporter()):
        yield
