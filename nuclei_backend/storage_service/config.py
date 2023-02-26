import pathlib
from importlib.resources import path
from typing import Final
import struct
from ...nuclei_backend.Config import OS


class Config(struct.Struct):
    if OS == "linux":
        TEMP_FOLDER = pathlib.Path(__file__).parent / "processing_temp"
        KUBO_PATH = pathlib.Path(__file__).parent / "linux_ipfs"
    elif OS == "windows":
        TEMP_FOLDER = pathlib.Path(__file__).parent.joinpath("processing_temp")
        KUBO_PATH = pathlib.Path(__file__).parent / "windows_ipfs.exe"
