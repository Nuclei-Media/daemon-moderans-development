from functools import total_ordering, lru_cache
import logging
import subprocess
import time

from fastapi import Depends, HTTPException
import os, pathlib

from ..storage_service.ipfs_model import DataStorage
from ..users.auth_utils import get_current_user
from ..users.user_handler_utils import get_db
from ..users.user_models import User
from .sync_user_cache import FileListener, RedisController, SchedulerController
from uuid import uuid4
from pathlib import Path


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


class UserDataExtraction:
    def __init__(self, user_id, db, cids: list):
        self.user_id = user_id
        self.session_id = uuid4()

        self.db = db
        self.user_data = get_user_cids(self.user_id, self.db)
        self.file_bytes = []
        self.cids = cids
        self.ipget_path = Path(__file__).parent / "ipget.exe"
        self.new_folder = (
            f"{Path(__file__).parent}\FILE_PLAYING_FIELD\{self.session_id}"
        )

    def download_file_ipfs(self, cid: str, filename: str):

        os.mkdir(self.new_folder)
        os.chdir(self.new_folder)
        file = f"{self.ipget_path} --node=local {cid} -o {filename} --progress=true"

        subprocess.Popen(str(f"{file}"))
        print(f"Downloading {filename} - {cid} - {self.session_id}")
        time.sleep(5)
        self.write_file_summary()

    def write_file_summary(self):
        # write a summary of the files downloaded into the self.session_id.internal.txt
        for _ in self.cids:
            if not os.path.isfile(f"{_.file_name}"):
                return False
            with open(f"{self.session_id}.internal.txt", "w") as _file:

                _file.write(f"\n{_.file_name}\n{_.file_size}\n{_.file_cid}\n")
                _file.close()

    def insurance(self) -> bool:
        for _ in self.cids:
            if not os.path.isfile(f"{_.file_name}"):
                return False
            _bytes = open(_.file_byte, "rb")
            if _bytes != _.file_size:
                return False
            del _bytes
        return True
