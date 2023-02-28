import pathlib
from importlib.resources import path
from typing import Literal
import struct
from ..Config import _Config


class Config(struct.Struct):
    if _Config.OS == "linux":
        TEMP_FOLDER: Literal = pathlib.Path(__file__).parent / "processing_temp"
        KUBO_PATH: Literal = pathlib.Path(__file__).parent / "linux_ipfs"
    elif _Config.OS == "windows":
        TEMP_FOLDER: Literal = pathlib.Path(__file__).parent.joinpath("processing_temp")
        KUBO_PATH: Literal = pathlib.Path(__file__).parent / "windows_ipfs.exe"
