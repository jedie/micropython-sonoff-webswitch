import time

for no in range(3, 0, -1):
    print('%i main.py wait...' % no)
    time.sleep(1)


print('gc.collect()')
import gc
gc.collect()


from webswitch import main
main()