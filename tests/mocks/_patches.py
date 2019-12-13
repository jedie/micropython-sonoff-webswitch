import traceback

import sys


def print_exception(e):
    traceback.print_exception(None, e, sys.exc_info()[2])


sys.print_exception = print_exception
