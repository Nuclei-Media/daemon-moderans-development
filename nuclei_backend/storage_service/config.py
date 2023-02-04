import pathlib
from importlib.resources import path
from typing import Final
import struct


# It's a class that defines a bunch of constants
class Config(struct.Struct):
    TEMP_FOLDER: Final = pathlib.Path(__file__).parent.joinpath("processing_temp")
    KUBO_PATH: Final = pathlib.Path(__file__).parent / "ipfs.exe"
