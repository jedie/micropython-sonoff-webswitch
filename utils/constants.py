from pathlib import Path

BASE_PATH = Path(__file__).parent.parent  # .../micropython-sonoff-webswitch/
SRC_PATH = Path(BASE_PATH, 'src')  # contains source *.py files
BDIST_PATH = Path(BASE_PATH, 'bdist')  # contains compiles *.mpy files
