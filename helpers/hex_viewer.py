import gc
import sys

import esp
import uasyncio
import utime
from micropython import const

LINE_COUNT = const(32)
CHUNK_SIZE = const(32)
BUFFER = bytearray(CHUNK_SIZE)


def hex_dump(offset=0):
    for line_num in range(LINE_COUNT):
        current_offset = offset + (line_num * CHUNK_SIZE)
        esp.flash_read(current_offset, BUFFER)

        print('%08x - %08x' % (current_offset, current_offset + CHUNK_SIZE - 1), end=' ')
        print(' '.join('%02x' % char for char in BUFFER), end=' ')
        print(
            ''.join(
                chr(char)
                if 32 <= char <= 126 and char not in (60, 62) else '.'
                for char in BUFFER
            )
        )

    gc.collect()


if __name__ == '__main__':
    hex_dump(offset=0)
