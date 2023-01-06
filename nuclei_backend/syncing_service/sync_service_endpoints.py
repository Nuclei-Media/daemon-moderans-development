import random
import time
import uuid

from fastapi import Depends
from functools import total_ordering, lru_cache

from ..users.auth_utils import get_current_user
from ..users.user_handler_utils import get_db
from ..users.user_models import User
from .sync_service_main import sync_router
from .sync_utils import (
    UserDataExtraction,
    get_collective_bytes,
    get_user_cids,
)
from .sync_user_cache import FileListener, RedisController, SchedulerController


@sync_router.get("/fetch/all")
async def dispatch_all(user: User = Depends(get_current_user), db=Depends(get_db)):

    cids = get_user_cids(user.id, db)
    queried_bytes = get_collective_bytes(user.id, db)

    files = UserDataExtraction(user.id, db, cids)
    try:
        for _ in range(len(cids)):
            files.download_file_ipfs(cids[_].file_cid, cids[_].file_name)
            time.sleep(1)
        # set up the redis cache
        FileListener(user.id).create_job(files.session_id, user.id, files.file_names)

    except Exception as e:
        raise e from e
    return {
        "message": "Dispatched",
        "cids": cids,
        "bytes": queried_bytes,
    }


@sync_router.get("/fetch/redis/all")
async def redis_cache_all(user: User = Depends(get_current_user), db=Depends(get_db)):
    # get all redis cache pertaining to the user
    all_files = RedisController().serialize_user_files(user.id)
    return {
        "files": all_files,
    }
