from __future__ import annotations

import contextlib
import datetime
import hashlib
import logging
import os
import pathlib
from fileinput import filename
from subprocess import PIPE, Popen, call
from typing import *
from uuid import UUID, uuid4

import gevent
import sqlalchemy.exc
from fastapi import Depends, HTTPException, UploadFile

# from nuclei_backend.users.auth_utils import get_current_user
from nuclei_backend.users.user_models import User
import magic

from ..users.auth_utils import get_current_user
from ..users.user_handler_utils import get_db
from .config import Config
from .ipfs_utils import *
from .main import storage_service

import hashlib
import logging
from typing import Dict

import json


class FileVerificationBroker:
    def __init__(self, file_types: Dict[str, str]):
        self.file_types = file_types
        self.magic = magic.Magic(mime=True)

    def verify_file(self, file: bytes):
        file_type = self.get_file_type(file)
        if file_type not in self.file_types.keys():
            logging.error(f"Unsupported file type: {file_type}")
            raise ValueError(f"Unsupported file type: {file_type}")

        if not self.check_file_hash(file, self.file_types[file_type]):
            logging.error("File hash check failed")
            raise ValueError("File hash check failed")

        return True

    @staticmethod
    def get_file_type(file: bytes):
        # code to determine the file type
        return magic.from_buffer(file, mime=True)

    @staticmethod
    def check_file_hash(file: bytes, expected_hash: str):
        # code to generate the file hash and compare with the expected hash
        return hash == expected_hash


def get_file_verification_broker(file_types: Dict[str, str]):
    config = json.load(Config.IMAGE)
    file_types = config["file_types"]
    return FileVerificationBroker(file_types)


@storage_service.post("/upload")
async def upload(
    file_name: UploadFile = File(),
    db=Depends(get_db),
    # file_verification_broker: FileVerificationBroker = Depends(
    #     get_file_verification_broker
    # ),
    current_user: User = Depends(get_current_user),
):
    file: bytes = file_name.file.read()
    cid = produce_cid(file, file_name)
    if not cid:
        raise HTTPException(status_code=400, detail="Failed to produce CID")

    _hash = generate_hash(cid)
    if not _hash:
        raise HTTPException(status_code=400, detail="Failed to generate hash")

    if not current_user:
        raise HTTPException(status_code=400, detail="User not found")

    users_id = current_user.id
    data_record = assemble_record(
        file,
        file_name,
        cid,
        users_id,
    )

    try:
        db.add(data_record)
        db.commit()

    except sqlalchemy.exc.IntegrityError:
        return {"message": "File already exists", "file_hash": _hash}

    except Exception as e:
        logging.error(e)
        raise HTTPException(status_code=500, detail="Internal Server Error") from e

    return {
        "cid": cid,
        "hash": _hash,
        "user_id": current_user.username,
        "status": "success",
    }


@storage_service.delete("/delete_all_records")
async def delete_all_records(db=Depends(get_db)):
    print("Deleting all records")
    try:
        # Get all records
        records = db.query(DataStorage).all()
        # Delete all records
        for record in records:
            db.delete(record)
        db.commit()
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal Server Error") from e
    return {"status": "success"}


# https://stribny.name/blog/fastapi-video/#:~:text=There%20is%20a%20simple%20mechanism,format%20bytes%3D1024000%2C2048000%20.
