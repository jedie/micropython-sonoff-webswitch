from unittest import mock


class MockOpen:

    def __init__(self, open_data):
        self._calls = []
        self.open_data = open_data

    def __call__(self, filename, mode):
        print(f'mocked open {filename!r}')
        self._calls.append((filename, mode))

        try:
            should_mode, content = self.open_data[filename]
        except KeyError:
            raise FileNotFoundError(filename)

        if mode != should_mode:
            raise AssertionError(
                f'Wrong file mode used: should: {should_mode!r} is: {mode!r}'
            )

        file_object = mock.mock_open(read_data=content).return_value
        file_object.__iter__.return_value = content.splitlines(True)
        return file_object
