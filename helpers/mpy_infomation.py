"""
    Print information about mpy implementation
    Origin code is from:
        http://docs.micropython.org/en/latest/reference/mpyfiles.html
"""

import sys

if __name__ == '__main__':
    sys_mpy = sys.implementation.mpy

    print(repr(sys_mpy))

    print('mpy version:', sys_mpy & 0xff)
    print('mpy flags:', end='')

    arch = [None, 'x86', 'x64',
            'armv6', 'armv6m', 'armv7m', 'armv7em', 'armv7emsp', 'armv7emdp',
            'xtensa', 'xtensawin'][sys_mpy >> 10]

    if arch:
        print(' -march=' + arch, end='')

    if sys_mpy & 0x100:
        print(' -mcache-lookup-bc', end='')

    if not sys_mpy & 0x200:
        print(' -mno-unicode', end='')

    print()
