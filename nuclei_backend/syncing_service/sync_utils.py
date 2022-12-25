import logging
import time

from fastapi import Depends, HTTPException
import os, pathlib

from ..storage_service.ipfs_model import DataStorage
from ..users.auth_utils import get_current_user
from ..users.user_handler_utils import get_db
from ..users.user_models import User


def get_user_cids(user_id, db) -> list:

    try:
        query = db.query(DataStorage).filter(DataStorage.owner_id == user_id).all()
        return query
    except Exception as e:
        logging.error(e)
        raise HTTPException(status_code=500, detail="Internal Server Error") from e


def get_collective_bytes(user_id, db):

    try:
        query = db.query(DataStorage).filter(DataStorage.owner_id == user_id).all()
        return sum(x.file_size for x in query)
    except Exception as e:
        logging.error(e)
        raise HTTPException(status_code=500, detail="Internal Server Error") from e


def paginate_using_gb(user_id, db, page_size=10, page=1):

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
    def __init__(self, user_id, cids: list):
        self.user_id: User = Depends(get_current_user)
        if not self.user_id:
            raise HTTPException(status_code=401, detail="Unauthorized")
        if self.user_id == user_id:

            self.db = Depends(get_db)
            self.user_data = get_user_cids(self.user_id, self.db)
            self.file_bytes = []
            self.cids = cids

            self.download_file_ipfs(self)
            self.insurance(self)

    def download_file_ipfs(self, cid: str, filename):  # ticket_identity
        if not os.path.isfile(f"{pathlib.Path(__file__).parent}\queued\{filename}"):
            os.popen(
                f"cd {pathlib.Path(__file__).parent}\queued "  # && mkdir {ticket_identity}
            )
            file = (
                pathlib.Path(__file__).parent
                / f"ipget.exe --node=local {cid}  -o  {pathlib.Path(__file__).parent}\queued\{filename} --progress=true"
            )
            os.popen(str(f"{file}"))
            time.sleep(1)
            return True

    def insurance(self) -> bool:
        for _ in self.cids:
            if not os.path.isfile(f"{_.file_name}"):
                return False
            _bytes = open(_.file_byte, "rb")
            if _bytes != _.file_size:
                return False
            del _bytes
        return True
