import gc

import esp
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


def search(offset, text):
    print('search for', repr(text))
    next_update = utime.time() + 1
    while True:
        try:
            esp.flash_read(offset, BUFFER)
        except OSError as e:
            print(b'Error: %s' % e)
            return 0

        if text in BUFFER:
            print('Found in block:', offset)
            return offset

        offset += CHUNK_SIZE

        if utime.time() >= next_update:
            print('Search:', offset)
            next_update = utime.time() + 1


if __name__ == '__main__':
    offset = search(offset=0, text='micropython')
    hex_dump(offset=offset)
