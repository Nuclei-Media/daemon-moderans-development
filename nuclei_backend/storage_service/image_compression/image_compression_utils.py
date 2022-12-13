import logging
import pathlib
import subprocess
from typing import Final
from uuid import uuid4

import PIL.Image
from fastapi import File

from ..CompressionBase import CompressionImpl

logger = logging.getLogger(__name__)


class CompressImage(CompressionImpl):
    def __init__(self, file: bytes, filename: str):

        super().__init__(app_path="image")

        self.file = file
        self.filename = filename
        self.compression_temp_file = self.save_to_temp(self.file, self.filename)

    def cleanup_compression_outcome(self):
        pathlib.Path(self.compression_temp_file[0]).unlink()

    def produce_compression(self) -> bytes:

        image = PIL.Image.open(self.compression_temp_file[0], "r")
        image.save(
            self.compression_temp_file[0],
            format="JPEG",
            optimize=True,
            progressive=True,
            quality=85,
        )

        with open(self.compression_temp_file[0], "rb") as f:
            compressed_file = f.read()

        return compressed_file
