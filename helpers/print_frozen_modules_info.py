"""
    Print the information from "frozen_modules_info.py"
    This file is generated with: "./utils/make_sdist.py"
    Used in "soft" OTA updates
"""

from frozen_modules_info import FROZEN_FILE_INFO

if __name__ == '__main__':
    print('Frozen modules info:\n')
    for filename, size, sha256 in FROZEN_FILE_INFO:
        print("%-22s %5s %s" % (filename, size, sha256))
