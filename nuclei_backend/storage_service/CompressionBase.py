import pathlib
from typing import Literal
from uuid import uuid4

from .ipfs_utils import assemble_record, produce_cid


class CompressionObject:
    # This class is responsible for compressing a file, saving it to a temporary location, committing it
    # to IPFS, and then cleaning up the temporary file
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
        """
        The function takes in a string argument and assigns it to the class variable app_path.

        The function then assigns the class variable path_variation to a dictionary with three keys:
        video, image, and misc.

        The values of the dictionary are tuples with two elements.

        The first element is a pathlib.Path object.

        The second element is a string.

        The pathlib.Path object is created by joining the parent directory of the file containing the
        function to the string "video_compression" and then joining the result to the string
        "_compression_temp".

        The pathlib.Path object is created by joining the parent directory of the file containing the
        function to the string "image_compression" and then joining the result to the string
        "_compression_temp".

        The pathlib.Path object is created by joining the parent directory of the file containing the
        function

        :param app_path: Literal["video", "image", "misc"]
        :type app_path: Literal["video", "image", "misc"]
        """
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
        """
        It saves a file to a temporary location and returns the path

        :param file_bytes: bytes
        :type file_bytes: bytes
        :param filename: the name of the file
        :return: A tuple of the temp_file and temp_file_identity
        """
        """Save file to temporary location and return path"""
        temp_dir = self.path_variation[self.app_path]
        temp_dir.mkdir(exist_ok=True)
        temp_file_identity = f"temp_file{uuid4()}{filename[int(filename.index('.')):]}"
        self.temp_file_identity = temp_file_identity
        temp_file = temp_dir / temp_file_identity
        temp_file.write_bytes(file_bytes)
        return (temp_file, temp_file_identity)

    def cleanup_file(self, temp_file: str) -> None:
        """
        > This function takes a file name as a parameter, and deletes the file
        
        :param temp_file: The path to the temporary file that will be created
        :type temp_file: str
        """
        pathlib.Path(temp_file).unlink()

    def temp_compression_save(self, file_path: str) -> str:
        """
        It takes a file path, finds the index of the word "temp_file" in the file path, and then returns a
        new file path with the word "compressed_temp" in place of "temp_file"
        
        :param file_path: str = "C:\Users\User\Desktop\temp_file_uuid.txt"
        :type file_path: str
        :return: The file path of the compressed file.
        """

        temp_file_index = file_path.find("temp_file")

        parsed_file_path: str = file_path[:temp_file_index]

        file_uuid: str = file_path[temp_file_index:][9:-4]

        return f"{parsed_file_path}\compressed_temp{file_uuid}"

    def commit_to_ipfs(self, file, filename: str, user, db) -> str:
        """
        It takes a file, a filename, a user, and a database, and returns a cid
        
        :param file: the file object
        :param filename: str = the name of the file
        :type filename: str
        :param user: User = current_user
        :param db: SQLAlchemy session
        """

        cid: str = produce_cid(file, filename)
        data_record = assemble_record(file, filename, cid, user.id)

        db.add(data_record)
        db.commit()
