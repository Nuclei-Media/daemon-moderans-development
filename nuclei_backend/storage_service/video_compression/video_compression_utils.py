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
    """
    It deletes a file

    :param temp_file: The name of the temporary file to create

    :type temp_file: str
    """
    pathlib.Path(temp_file).unlink()


def save_to_temp(file_bytes: bytes) -> str:
    """
    It takes a byte array, creates a temporary directory if it doesn't exist, creates a temporary file
    in that directory, writes the byte array to the file, and returns the path to the file

    :param file_bytes: the bytes of the video file
    :type file_bytes: bytes
    :return: The path to the temporary file.
    """
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
    """
    It takes a file path, finds the index of the word "temp_file", then returns the file path with the
    word "compressed_temp" in place of "temp_file".

    :param file_path: str = "C:/Users/User/Desktop/temp_file_uuid.mp4"
    :type file_path: str
    :return: The file path of the compressed file.
    """

    temp_file_index = file_path.find("temp_file")

    parsed_file_path: str = file_path[:temp_file_index]

    file_uuid: str = file_path[temp_file_index:][9:-4]

    return f"{parsed_file_path}\compressed_temp{file_uuid}.mp4"


class CompressVideoInterface:
    def __init__(self, rate: str, file: bytes):
        """
        The function takes a string and a bytes object as arguments, and assigns them to the class
        attributes rate and file. It then assigns a dictionary to the class attribute rates.

        :param rate: The rate of the audio file
        :type rate: str
        :param file: The file to be converted
        :type file: bytes
        """
        self.rate = rate
        self.file = file
        self.rates: Final = {
            "low": 24,
            "medium": 28,
            "high": 30,
            "lossless": 26,
        }


class CompressVideo(CompressVideoInterface):
    def __init__(self, rate: str, file: bytes):
        """
        It takes a file and a rate, and then it saves the file to a temporary location, and then it
        returns the temporary location

        :param rate: str
        :type rate: str
        :param file: The file that is being compressed
        :type file: bytes
        """

        super().__init__(rate, file)
        self.rate = self.rates[rate]
        self.file = file
        self.compression_temp_file = temp_compression_save(self.file)

    def produce_compression(self) -> bytes:
        """
        It takes a file, compresses it, and returns the compressed file as a byte object.
        :return: The compressed file
        """

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
        """
        It takes a file, compresses it, generates a CID, creates a database record, and then deletes the
        file

        :param file: The file object that was uploaded
        :param filename: str = "test.txt"
        :param user: User = current_user
        :param db: SQLAlchemy session
        """

        cid: str = produce_cid(file, filename)
        data_record = assemble_record(file, filename, cid, user.id)

        db.add(data_record)
        db.commit()

        cleanup_file(self.compression_temp_file)
        cleanup_file(self.file)
