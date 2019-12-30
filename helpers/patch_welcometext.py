import esp

SECTOR_SIZE = const(4096)
BUFFER = memoryview(bytearray(SECTOR_SIZE))

if __name__ == '__main__':
    sector_no = 151  # sector with: 'MicroPython v1.12 on 2019-12-20;...'
    byte_offset = sector_no * SECTOR_SIZE  # byte offset: 618496 0x97000
    print('sector no: %i -> byte offset: %i 0x%x' % (sector_no, byte_offset, byte_offset))

    # check fw with not changed content:
    # size: 619812
    # md5: 439de24004683e779dfff08f96df900d
    print(esp.check_fw())  # will return True

    # read the 4KB sector:

    esp.flash_read(byte_offset, BUFFER)
    # print(bytearray(BUFFER))
    print(bytearray(BUFFER[0x38a:0x3aa]))  # bytearray(b'MicroPython v1.12 on 2019-12-20;')

    # Change the content:
    BUFFER[0x38a:0x3aa] = b'MICROPYTHON v9.99 on 2200-12-24;'
    esp.flash_erase(151)
    esp.flash_write(byte_offset, BUFFER)

    # Check the content:
    esp.flash_read(byte_offset, BUFFER)
    print(bytearray(BUFFER[0x38a:0x3aa]))

    # check fw with changed content:
    # size: 619812
    # md5: 8696b82c53ea091bd2d6cd9a24796f3e
    print(esp.check_fw())  # False

    # Change back to origin:

    BUFFER[0x38a:0x3aa] = b'MicroPython v1.12 on 2019-12-20;'
    esp.flash_erase(151)
    esp.flash_write(byte_offset, BUFFER)

    # Check flash:
    esp.flash_read(byte_offset, BUFFER)
    print(bytearray(BUFFER[0x38a:0x3aa]))

    # check fw with not changed content:
    # size: 619812
    # md5: 439de24004683e779dfff08f96df900d
    print(esp.check_fw())
