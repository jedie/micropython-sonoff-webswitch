import gc
import sys

sys.modules.clear()

gc.collect()

alloc = gc.mem_alloc() / 1024
free = gc.mem_free() / 1024

print('\nRAM total: {total:.2f} KB, used: {alloc:.2f} KB, free: {free:.2f} KB\n'.format(
    total=alloc + free,
    alloc=alloc,
    free=free
))

gc.collect()

import micropython
# see:
# http://docs.micropython.org/en/latest/reference/constrained.html#reporting
micropython.mem_info(1)
