from __future__ import annotations

import contextlib
import datetime
import logging
import os
import os.path
import pathlib
from subprocess import PIPE, Popen, call
from typing import *
from uuid import UUID, uuid4

import gevent
from fastapi import File, UploadFile
from sqlalchemy.orm import Session
from typing_extensions import LiteralString

from nuclei_backend.users.user_models import User

from .config import Config
from .ipfs_model import DataStorage
from .ipfs_schema import IpfsCreate


def ensure_dir(path: str) -> None:
    """
    > If the directory doesn't exist, create it

    Arguments:

    * `path`: str
    """

    pathlib.Path(path).mkdir(parents=True, exist_ok=True)


def save_temp_file(file, filename: str) -> str:
    """
    It takes a file and a filename, saves the file to a temporary folder, and returns the path to the
    file

    Arguments:

    * `file`: The file that was uploaded
    * `filename`: The name of the file that was uploaded.

    Returns:

    The file path of the file that was saved.
    """

    unique_id = str(uuid4())
    _filename = f"filename{unique_id}{filename[-4:]}"
    _file_path = os.path.join(Config.TEMP_FOLDER, _filename)

    with open(_file_path, "wb") as f:
        f.write(file)

    return _file_path


def remove(path):
    os.remove(path)


def generate_hash(cid: LiteralString) -> str:
    """
    It generates a hash of a file on IPFS using the IPFS CLI

    :param cid: The CID of the file you want to get the hash of
    :type cid: LiteralString
    :return: The hash of the file.
    """

    path = str(Config.TEMP_FOLDER)
    unique_id = str(uuid4())
    _bat_path = os.path.join(Config.TEMP_FOLDER, f"hash{unique_id}.bat")
    _buffer_path = os.path.join(Config.TEMP_FOLDER, f"hash{unique_id}.txt")

    with open(_bat_path, "w") as f:
        f.write(rf"cd {path}")
        f.write("\n")
        f.write(rf"ipfs ls -v {cid} > hash{unique_id}.txt")
    call(_bat_path)

    with open(_buffer_path, "r") as f:
        hash = f.read().strip()

    remove(_bat_path)
    remove(_buffer_path)

    return hash


def produce_cid(file: bytes, filename: str) -> LiteralString:
    """
    It takes a file and a filename, saves the file to a temporary folder, runs a command in the terminal
    to add the file to IPFS, and returns the CID of the file.

    Arguments:

    * `file`: bytes
    * `filename`: The name of the file you want to upload

    Returns:

    The CID of the file.
    """

    print(Config.TEMP_FOLDER)
    if not os.path.exists(Config.TEMP_FOLDER):
        ensure_dir(Config.TEMP_FOLDER)
    try:
        path = str(Config.TEMP_FOLDER)
        unique_id = str(uuid4())
        _bat_path = os.path.join(Config.TEMP_FOLDER, f"cid{unique_id}.bat")
        _buffer_path = os.path.join(Config.TEMP_FOLDER, f"cid{unique_id}.txt")
        _temp_file_path = save_temp_file(file, filename)
    except Exception as e:
        raise e
    print(_temp_file_path)

    with open(_bat_path, "w") as f:
        f.write(rf"cd {path}")
        f.write("\n")
        f.write(
            rf"ipfs add --quiet --pin {_temp_file_path} > {path}\cid{unique_id}.txt"
        )
    call(_bat_path)

    with open(_buffer_path, "r") as f:
        cid = f.read().strip()

    remove(_bat_path)
    remove(_buffer_path)
    pathlib.Path(_temp_file_path).unlink()

    return cid


def assemble_record(file: bytes, filename: str, cid: str, owner_id: int = None):
    """It takes a file, filename, and cid, and returns a DataStorage object with the file_name, file_cid,
    file_hash, file_size, file_type, file_upload_date, and owner_id attributes

    Parameters
    ----------
    file : bytes
        bytes
    filename : str
        The name of the file
    cid : str
        The content identifier of the file.
    owner_id : int
        The user who uploaded the file

    Returns
    -------
        A DataStorage object

    """

    return DataStorage(
        file_name=filename,
        file_cid=cid,
        file_hash=generate_hash(cid),
        file_size=len(file),
        file_type=os.path.splitext(file)[1],
        file_upload_date=datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        owner_id=owner_id,
    )
