

import machine

rtc = machine.RTC()
i = 1
while True:
    try:
        rtc.memory(b'X' * i)
    except Exception as e:
        print('Error:', e)
        print(len(rtc.memory()), 'Bytes')
        print(rtc.memory())
        break
    else:
        i += 1
