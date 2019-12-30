import esp
import lwip
import network
import uctypes
from flashbdev import bdev

FIRMWARE_START = const(0x40200000)

def main():

    print('sector size:', bdev.SEC_SIZE)

    ROM = uctypes.bytearray_at(FIRMWARE_START, 16)
    fid = esp.flash_id()

    print("FlashROM:")
    print("Flash ID: %x (Vendor: %x Device: %x)" % (fid, fid & 0xff, fid & 0xff00 | fid >> 16))

    print("Flash bootloader data:")
    SZ_MAP = {0: "512KB", 1: "256KB", 2: "1MB", 3: "2MB", 4: "4MB"}
    FREQ_MAP = {0: "40MHZ", 1: "26MHZ", 2: "20MHz", 0xf: "80MHz"}
    print("Byte @2: %02x" % ROM[2])
    print(
        "Byte @3: %02x (Flash size: %s Flash freq: %s)" %
        (ROM[3], SZ_MAP.get(
            ROM[3] >> 4, "?"), FREQ_MAP.get(
            ROM[3] & 0xf)))
    print("Firmware checksum:")
    print(esp.check_fw())

    # esp8266-20191220-v1.12.bin
    # 619828 Bytes
    # 620f7bca01ab221c0d1bd56f889c6008

    ROM = uctypes.bytearray_at(FIRMWARE_START, 16)
    print(repr(ROM))

    import errno


if __name__ == '__main__':
    main()
