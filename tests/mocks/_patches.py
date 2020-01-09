"""
    Expand existing python modules
"""
import builtins
import gc
import sys
import traceback

import context


def _print_exception(e):
    traceback.print_exception(None, e, sys.exc_info()[2])


sys.print_exception = _print_exception


def _mem_free():
    return 1000


gc.mem_free = _mem_free


def _mem_alloc():
    return 1000


gc.mem_alloc = _mem_alloc

builtins.__DEBUG__ = True


def no_exit(no=None):
    print(f'sys.exit({no!r}) called!')


sys.exit = no_exit

# Save context values and defauls for NonSharedContext.__init__()
_default_context = dict(
    (attr, getattr(context.Context, attr))
    for attr in dir(context.Context)
    if not attr.startswith('_')
)
# print(_default_context)


class NonSharedContext:
    """
    Same as context.Context, but all attributes are init in __init__()
    So they are reset on every test method
    """

    def __init__(self):
        self.reset()

    def reset(self):
        print('NonSharedContext.reset():')
        for attr, value in _default_context.items():
            print(f'\t{attr} = {value!r}')
            setattr(self, attr, value)


context.Context = NonSharedContext
