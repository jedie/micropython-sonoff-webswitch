import gc

import esp
import utime
from micropython import const

LINE_COUNT = const(6)
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
    print('search for %r start with offset 0x%x' % (text, offset))

    offset_step = CHUNK_SIZE - len(text)

    if offset_step <= 0:
        raise AssertionError('Search text too large: increase CHUNK_SIZE!')

    def print_throughput():
        duration = utime.time() - start_time
        if duration == 0:
            throughput = -1
        else:
            throughput = (offset - start_offset) / duration / 1024
        print(
            '(Search duration: %i sec. - %i KBytes/sec' % (duration, throughput)
        )

    flash_size = esp.flash_size()
    start_offset = offset
    end_researched = False
    start_time = utime.time()
    next_update = start_time + 1
    while True:
        if offset + CHUNK_SIZE > flash_size:
            # Search to esp.flash_size(), but don't go beyond.
            offset = flash_size - CHUNK_SIZE
            end_researched = True

        try:
            esp.flash_read(offset, BUFFER)
        except OSError as e:
            print('Read flash error: %s at 0x%x - 0x%x' % (e, offset, offset + CHUNK_SIZE))
            return -1

        if text in BUFFER:
            print('Found in 0x%x !' % offset, end=' ')
            print_throughput()
            return offset

        if utime.time() >= next_update:
            print('Search: 0x%x ...' % offset, end=' ')
            print_throughput()
            next_update = utime.time() + 1

        if end_researched:
            print('Memory end researched, searched up to 0x%x' % (offset + CHUNK_SIZE))
            print_throughput()
            return -1

        offset += offset_step


if __name__ == '__main__':
    print('esp.flash_user_start(): 0x%x' % (esp.flash_user_start()))
    print('esp.flash_size()......: 0x%x' % (esp.flash_size()))

    offset = 0x0
    while True:
        offset = search(offset=offset, text='micropython')
        if offset == -1:
            # not found or end researched
            break
        hex_dump(offset=offset)
        offset += (CHUNK_SIZE * LINE_COUNT) - 1
