from os import mkdir, remove, stat  # noqa


class _FakeOsUname:
    sysname = 'name of underlying system'
    nodename = 'network name'
    release = 'version of underlying system'
    version = 'MicroPython version and build date'
    machine = 'an identifier for underlying hardware (eg board, CPU)'


def uname():
    """
    http://docs.micropython.org/en/latest/library/uos.html#uos.uname
    """
    return _FakeOsUname
