

class MicroPythonOpen:
    def __init__(self, origin_open, filename, mode):
        self.origin_open = origin_open
        self.filename = filename
        self.mode = mode

    def __enter__(self):
        print(f'open {self.filename!r} mode: {self.mode!r}')
        self.f = self.origin_open(self.filename, self.mode)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.f.close()

    def readinto(self, buffer, size):
        """
        FIXME: Is there is a easier way to extend readinto() with size argument?
        """
        content = self.f.read(size)

        if not isinstance(buffer, memoryview):
            raise NotImplementedError

        obj = buffer.obj
        if not isinstance(obj, bytearray):
            raise NotImplementedError

        # FIXME: How to easier 'transfer' the content into existing bytearray?
        for pos, char in enumerate(content):
            obj[pos] = char

        return len(content)


class MockOpen:
    """
    Replace builtin open currently only to add a `size` argument in `readinto` method.
    """

    def __init__(self, origin_open):
        self.origin_open = origin_open

    def __call__(self, filename, mode):
        print(f'mocked open {filename!r}')
        return MicroPythonOpen(self.origin_open, filename, mode)
