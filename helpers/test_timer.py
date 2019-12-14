import machine
import utime


def timer_callback(timer):
    print('called:', utime.time(), timer)


timer = machine.Timer(-1)
timer.deinit()
print('init', utime.time())
x = timer.init(
    period=1000,
    mode=machine.Timer.ONE_SHOT,
    callback=timer_callback
)
print(x)
