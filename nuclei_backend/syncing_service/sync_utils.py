import logging
import subprocess
import typing
from typing import Optional

from fastapi import Depends, HTTPException

from ..storage_service.ipfs_model import DataStorage
from ..users.auth_utils import get_current_user
from ..users.user_handler_utils import get_db
from ..users.user_models import User


def get_user_cids(user_id, db) -> list:
    """
    It takes a user_id and a database session as input, and returns a list of DataStorage objects
    that have the same owner_id as the user_id

    Arguments:

    * `user_id`: int
    * `db`: Session = Depends(get_db)

    Returns:

    A list of DataStorage objects
    """

    try:
        query = db.query(DataStorage).filter(DataStorage.owner_id == user_id).all()
        return query
    except Exception as e:
        logging.error(e)
        raise HTTPException(status_code=500, detail="Internal Server Error") from e


def get_collective_bytes(user_id, db):
    """
    It takes a user_id and a database session as input, and returns the sum of the file_size of all the
    DataStorages that have the same owner_id as the user_id

    Arguments:

    * `user_id`: int
    * `db`: Session = Depends(get_db)

    Returns:

    The sum of the file_size of all the records that belong to the user_id
    """

    try:
        query = db.query(DataStorage).filter(DataStorage.owner_id == user_id).all()
        return sum(x.file_size for x in query)
    except Exception as e:
        logging.error(e)
        raise HTTPException(status_code=500, detail="Internal Server Error") from e


def paginate_using_gb(user_id, db, page_size=10, page=1):
    """
    A function that divides the records into a nested list with the size of the nested
    list's record being determined through the files record's file_size adding up to a gigabyte

    Arguments:

    * `user_id`: the user's id
    * `db`: a database connection
    * `page_size`: the number of records per page
    * `page`: int = 1

    Returns:

    A list of lists of DataStorage objects.
    """

    try:
        query = db.query(DataStorage).filter(DataStorage.owner_id == user_id).all()
        if not query:
            raise HTTPException(status_code=404, detail="No records found")
        page = page - 1
        start = page * page_size
        end = start + page_size
        return query[start:end]
    except Exception as e:
        logging.error(e)
        raise HTTPException(status_code=500, detail="Internal Server Error") from e


class UserDataExtraction:
    def __init__(self, user_id):
        """
        I'm trying to get the user_id from the token, and then use that user_id to get the user's cids
        from the database

        Arguments:

        * `user_id`: User = Depends(get_current_user)
        """
        self.user_id: User = Depends(get_current_user)
        if not self.user_id:
            raise HTTPException(status_code=401, detail="Unauthorized")
        if self.user_id == user_id:

            self.db = Depends(get_db)
            self.user_data = get_user_cids(self.user_id, self.db)
            self.file_bytes = []

    def file_bytes_serializer(self):
        # use file_byte_generator to get the file_bytes and append it to the file_bytes list
        # return the file_bytes list

        for file_byte in self.file_byte_generator():
            self.file_bytes.append(
                {
                    "user_id": self.user_id,
                    "file_name": self.user_data.file_name,
                    "file_type": self.user_data.file_type,
                    "file_bytes": file_byte,
                }
            )

    def download_file_ipfs(self, cid: str, filename):  # ticket_identity
        import os, pathlib

        os.popen(
            f"cd {pathlib.Path(__file__).parent}\queued "  # && mkdir {ticket_identity}
        )
        file = (
            pathlib.Path(__file__).parent
            / f"ipget.exe {cid} -o {pathlib.Path(__file__).parent}\queued\{filename} --progress=true"
        )
        os.popen(str(f"{file}"))

    def file_byte_generator(self):
        # generator which yields the file bytes from the function download_file_ipfs
        for record in self.user_data:
            yield self.download_file_ipfs(record.cid, record)

    def get_file_bytes(self):
        return self.file_bytes
