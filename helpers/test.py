import machine
import micropython

micropython.mem_info()

for i in range(10):
    print(i, id(machine.RTC()))

micropython.mem_info()
