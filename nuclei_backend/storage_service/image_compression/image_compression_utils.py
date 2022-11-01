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
    """Compress video with ffmpeg"""

    def __init__(self, file: bytes, filename: str):
        """
        Initialise the class with the rate and file to compress

        :param rate: The rate to compress the video at
        :param file: The file to compress

        """
        super().__init__(app_path="image")

        self.file = file
        self.filename = filename
        self.compression_temp_file = self.save_to_temp(self.file, self.filename)

    def cleanup_compression_outcome(self):
        pathlib.Path(self.compression_temp_file[0]).unlink()

    def produce_compression(self) -> bytes:
        """Produce the compression"""

        image = PIL.Image.open(self.compression_temp_file[0])
        image.save(self.compression_temp_file[0], "jpeg", quality=85)

        with open(self.compression_temp_file[0], "rb") as f:
            compressed_file = f.read()

        return compressed_file
