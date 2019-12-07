"""
    Delete 'main.py' and hard reset, for experiments via REPL
"""

import sys
sys.modules.clear()

import gc
gc.collect()

print('DELETE: main.py !!!')
import uos
uos.remove('main.py')

print('Hard reset !')

import machine
machine.reset()

import utime
utime.sleep(1)

print('sys.exit()')
import sys
sys.exit()
