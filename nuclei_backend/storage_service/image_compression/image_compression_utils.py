import logging
import pathlib
import subprocess
from typing import Final
from uuid import uuid4

import PIL.Image
from fastapi import File

from ..CompressionBase import CompressionImpl

logger = logging.getLogger(__name__)


def supported_image_types() -> list:
    """Return the supported image types which is eveyr image type"""
    return ["jpg", "jpeg", "png", "gif", "bmp", "tiff", "webp", "svg", "ico", "heic"]


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

        image = PIL.Image.open(
            self.compression_temp_file[0], "r", formats=supported_image_types()
        )
        image.save(
            self.compression_temp_file[0],
            # get the file extension of the file from the file name
            format=self.filename.split(".")[-1],
            optimize=True,
            progressive=True,
            quality=85,
        )

        with open(self.compression_temp_file[0], "rb") as f:
            compressed_file = f.read()

        return compressed_file
