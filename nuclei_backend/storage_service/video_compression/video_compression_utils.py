import logging
import pathlib
import subprocess
from typing import Final
from uuid import uuid4

import ffmpeg
from fastapi import File

from ..ipfs_utils import *

logger = logging.getLogger(__name__)


def cleanup_file(temp_file: str) -> None:
    """Remove temporary file"""
    pathlib.Path(temp_file).unlink()


def save_to_temp(file_bytes: bytes) -> str:
    """Save file to temporary location and return path"""
    try:
        temp_dir = pathlib.Path(__file__).parent.absolute() / "_compression_temp"
        temp_dir.mkdir(exist_ok=True)
        temp_file = temp_dir / f"temp_file{uuid4()}.mp4"
        temp_file.write_bytes(file_bytes)
        return str(temp_file)
    except Exception as e:
        print(e)
        return None


def temp_compression_save(file_path: str) -> str:
    """Save file to temporary location and return path"""

    temp_file_index = file_path.find("temp_file")

    parsed_file_path: str = file_path[:temp_file_index]

    file_uuid: str = file_path[temp_file_index:][9:-4]

    return f"{parsed_file_path}\compressed_temp{file_uuid}.mp4"


class CompressVideoInterface:
    """Compress video interface"""

    def __init__(self, rate: str, file: bytes):
        """Initialise compress video interface"""
        self.rate = rate
        self.file = file
        self.rates: Final = {
            "low": 24,
            "medium": 28,
            "high": 30,
            "lossless": 26,
        }


class CompressVideo(CompressVideoInterface):
    """Compress video with ffmpeg"""

    def __init__(self, rate: str, file: bytes):
        """
        Initialise the class with the rate and file to compress

        :param rate: The rate to compress the video at
        :param file: The file to compress

        """
        super().__init__(rate, file)
        self.rate = self.rates[rate]
        self.file = file
        self.compression_temp_file = temp_compression_save(self.file)

    def produce_compression(self) -> bytes:
        """Produce the compression"""

        result = (
            ffmpeg.input(str(self.file))
            .output(
                filename=self.compression_temp_file,
                vcodec="libx264",
                crf=self.rate,
            )
            .run(
                quiet=True,
            )
        )

        with open(self.compression_temp_file, "rb") as f:
            compressed_file = f.read()

        return compressed_file

    def commit_to_ipfs(self, file, filename, user, db) -> str:
        """Commit the compressed file to IPFS"""

        cid: str = produce_cid(file, filename)
        data_record = assemble_record(file, filename, cid, user.id)

        db.add(data_record)
        db.commit()

        cleanup_file(self.compression_temp_file)
        cleanup_file(self.file)
