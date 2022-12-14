import random
import uuid

from fastapi import Depends

from ..users.auth_utils import get_current_user
from ..users.user_handler_utils import get_db
from ..users.user_models import User
from .sync_service_main import socket_manager, sync_router
from .sync_utils import (
    UserDataExtraction,
    get_collective_bytes,
    get_user_cids,
    paginate_using_gb,
)


@sync_router.get("/dispatch")
async def dispatch_files(
    user: User = Depends(get_current_user),
    db=Depends(get_db),
):
    request_id = str(uuid.uuid4())
    request_id = request_id[random.randint(1, 40) : random.randint(41, 80)] = user.id
    cids = get_user_cids(user.id, db)
    queried_bytes = get_collective_bytes(user.id, db)

    # paginate and dispatch the files through the socketio connection

    return {"message": "Dispatched", "request id": request_id}


@sync_router.get("/dispatch/all")
def dispatch_all(
    user: User = Depends(get_current_user),
    db=Depends(get_db),
):

    cids = get_user_cids(user.id, db)
    queried_bytes = get_collective_bytes(user.id, db)

    files = UserDataExtraction(user.id)
    try:
        for _ in range(len(cids)):
            files.download_file_ipfs(cids[_].file_cid, cids[_].file_name)
    except Exception as e:
        raise e from e
    # paginate and dispatch the files through the socketio connection
    return {
        "message": "Dispatched",
        "cids": cids,
        "bytes": queried_bytes,
    }
