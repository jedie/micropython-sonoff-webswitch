"""
    Expand existing python modules
"""
import builtins
import gc
import sys
import traceback


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
