import pathlib
from typing import Literal
from uuid import uuid4

from .ipfs_utils import assemble_record, produce_cid


class CompressionObject:
    def produce_compression(self) -> bytes:
        ...

    def commit_to_ipfs(self, file, filename, user, db) -> str:
        ...

    def cleanup_file(temp_file: str) -> None:
        ...

    def save_to_temp(file_bytes: bytes) -> str:
        ...

    def temp_compression_save(file_path: str) -> str:
        ...

    def commit_to_ipfs(self, filename, user, db) -> str:
        ...

    def cleanup_file(temp_file: str) -> None:
        ...


class CompressionImpl(CompressionObject):
    def __init__(self, app_path: Literal["video", "image", "misc"]):
        """Initialise the class with the rate and file to compress"""
        print("app path ", app_path)
        self.app_path = app_path
        self.path_variation = {
            "video": (
                pathlib.Path(__file__).parent.joinpath("video_compression")
                / "_compression_temp",
            ),
            "image": (
                pathlib.Path(__file__).parent.joinpath("image_compression")
                / "_compression_temp"
            ),
            "misc": (
                pathlib.Path(__file__).parent.joinpath("misc_compression")
                / "_compression_temp"
            ),
        }

    def save_to_temp(self, file_bytes: bytes, filename) -> tuple:
        """Save file to temporary location and return path"""
        temp_dir = self.path_variation[self.app_path]
        temp_dir.mkdir(exist_ok=True)
        temp_file_identity = f"temp_file{uuid4()}{filename[int(filename.index('.')):]}"
        self.temp_file_identity = temp_file_identity
        temp_file = temp_dir / temp_file_identity
        temp_file.write_bytes(file_bytes)
        return (temp_file, temp_file_identity)

    def cleanup_file(self, temp_file: str) -> None:

        """Remove temporary file"""

        pathlib.Path(temp_file).unlink()

    def temp_compression_save(self, file_path: str) -> str:
        """Save file to temporary location and return path"""

        temp_file_index = file_path.find("temp_file")

        parsed_file_path: str = file_path[:temp_file_index]

        file_uuid: str = file_path[temp_file_index:][9:-4]

        return f"{parsed_file_path}\compressed_temp{file_uuid}"

    def commit_to_ipfs(self, file, filename: str, user, db) -> str:
        """Commit the compressed file to IPFS"""

        cid: str = produce_cid(file, filename)
        data_record = assemble_record(file, filename, cid, user.id)

        db.add(data_record)
        db.commit()
