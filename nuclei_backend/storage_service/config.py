import pathlib
from importlib.resources import path
from typing import Final
import struct
from ..Config import OsConfig


class Config(struct.Struct):
    if OsConfig.OS == "linux":
        TEMP_FOLDER = pathlib.Path(__file__).parent / "processing_temp"
        KUBO_PATH = pathlib.Path(__file__).parent / "linux_ipfs"
    elif OsConfig.OS == "windows":
        TEMP_FOLDER = pathlib.Path(__file__).parent.joinpath("processing_temp")
        KUBO_PATH = pathlib.Path(__file__).parent / "windows_ipfs.exe"
