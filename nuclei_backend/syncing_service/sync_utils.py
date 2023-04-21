import contextlib
from functools import lru_cache
import logging
import shutil
import subprocess
import time

from fastapi import HTTPException
import os, pathlib

from ..storage_service.ipfs_model import DataStorage
from uuid import uuid4
from pathlib import Path
import json
import contextlib


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


from ..Config import OsConfig


class UserDataExtraction:
    def __init__(self, user_id, db, cids: list):
        self.user_id = user_id
        self.session_id = uuid4()

        self.db = db
        self.user_data = get_user_cids(self.user_id, self.db)
        self.file_bytes = []
        self.cids = cids
        if OsConfig.OS == "windows":
            self.ipget_path = Path(__file__).parent / "utils\ipget.exe"
            self.new_folder = (
                f"{Path(__file__).parent}\FILE_PLAYING_FIELD\{self.session_id}"
            )
        if OsConfig.OS == "linux":
            self.ipget_path = Path(__file__).parent / "utils/ipget"
            self.new_folder = (
                f"{Path(__file__).parent}/FILE_PLAYING_FIELD/{self.session_id}"
            )
        print(f"ipget path{self.ipget_path}")

    def download_file_ipfs(self):
        if OsConfig.OS == "windows":
            with contextlib.suppress(PermissionError):
                os.mkdir(self.new_folder)
                os.chdir(self.new_folder)
                for _ in self.cids:
                    try:
                        file = f"{self.ipget_path} --node=local {_.file_cid} -o {_.file_name} --progress=true"

                        subprocess.Popen(str(f"{file}"))
                        print(
                            f"Downloading {_.file_name} - {_.file_cid} - {self.session_id}"
                        )
                        time.sleep(5)
                    except Exception as e:
                        print(f"this is the error: {e}")
                        raise e
                self.write_file_summary()

        if OsConfig.OS == "linux":
            with contextlib.suppress(PermissionError):
                os.mkdir(self.new_folder)
                os.chdir(self.new_folder)
                for _ in self.cids:
                    try:
                        file = f"{self.ipget_path} --node=local {_.file_cid} -o {_.file_name} --progress=true"

                        os.system(str(f"{file}"))
                        print(
                            f"Downloading {_.file_name} - {_.file_cid} - {self.session_id}"
                        )
                        time.sleep(5)
                    except Exception as e:
                        print(f"this is the error: {e}")
                        raise e
                self.write_file_summary()

    def write_file_summary(self):
        if OsConfig.OS == "windows":
            with contextlib.suppress(PermissionError):
                file_sum = {
                    _.file_name: {
                        "file_name": _.file_name,
                        "file_cid": _.file_cid,
                        "file_size": _.file_size,
                    }
                    for _ in self.cids
                }
                with open(f"{self.session_id}.internal.json", "w") as f:
                    json.dump(file_sum, f)
        if OsConfig.OS == "linux":
            with contextlib.suppress(PermissionError):
                file_sum = {
                    _.file_name: {
                        "file_name": _.file_name,
                        "file_cid": _.file_cid,
                        "file_size": _.file_size,
                    }
                    for _ in self.cids
                }
                with open(f"{self.session_id}.internal.json", "w") as f:
                    json.dump(file_sum, f)

    def insurance(self) -> bool:
        for _ in self.cids:
            if not os.path.isfile(f"{_.file_name}"):
                return False
            _bytes = open(_.file_byte, "rb")
            if _bytes != _.file_size:
                return False
            del _bytes
        return True

    def cleanup(self):
        with contextlib.suppress(PermissionError):
            os.chdir(pathlib.Path(self.new_folder).parent)

            shutil.rmtree(
                pathlib.Path(self.new_folder),
                ignore_errors=True,
            )
