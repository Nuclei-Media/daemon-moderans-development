import random
import time
import uuid
from functools import lru_cache, total_ordering

from fastapi import Depends

from ..storage_service.ipfs_model import DataStorage
from ..users.auth_utils import get_current_user
from ..users.user_handler_utils import get_db
from ..users.user_models import User
from .sync_service_main import sync_router
from .sync_user_cache import FileListener, RedisController, SchedulerController
from .sync_utils import UserDataExtraction, get_collective_bytes, get_user_cids


@sync_router.get("/fetch/all")
async def dispatch_all(user: User = Depends(get_current_user), db=Depends(get_db)):

    cids = get_user_cids(user.id, db)
    queried_bytes = get_collective_bytes(user.id, db)

    files = UserDataExtraction(user.id, db, cids)
    try:
        files.download_file_ipfs()
        FileListener(user.id, files.session_id).file_listener()

    except Exception as e:
        print(e)
    return {
        "message": "Dispatched",
        "cids": cids,
        "bytes": queried_bytes,
    }


@sync_router.get("/fetch/redis/all")
async def redis_cache_all(user: User = Depends(get_current_user), db=Depends(get_db)):
    # get all redis cache pertaining to the user
    all_files = RedisController().get_files(str(user.id))
    return {
        "files": all_files,
    }


@sync_router.get("/fetch/redis/clear")
async def redis_cache_clear(user: User = Depends(get_current_user), db=Depends(get_db)):
    return RedisController().clear_cache(str(user.id))


@sync_router.get("/fetch/redis/test")
async def redis_cache_test(user: User = Depends(get_current_user), db=Depends(get_db)):
    user_id = "user_1"
    session_id = "session_1"
    # redis test
    redis = RedisController()
    redis.initialise_user(user_id)
    redis.set_upload_user_files(user_id, ["file_1", "file_2", "file_3"])
    return {redis.serialize_user_files(user_id)}


@sync_router.get("/all")
def return_all(user: User = Depends(get_current_user), db=Depends(get_db)):
    user_data = (
        db.query(User).filter(User.id == user.id).all(),
        db.query(DataStorage).filter(DataStorage.owner_id == user.id).all(),
    )

    return {
        "user": user_data,
    }
