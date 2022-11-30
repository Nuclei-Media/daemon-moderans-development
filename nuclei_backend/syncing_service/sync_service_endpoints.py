import random
from .sync_service_main import sync_router, socket_manager
from .sync_utils import get_user_cids, get_collective_bytes, paginate_using_gb
from .sync_utils import UserDataExtraction

from fastapi import Depends
from ..users.auth_utils import get_current_user
from ..users.user_models import User
from ..users.user_handler_utils import get_db
import uuid


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
    pages = paginate_using_gb(queried_bytes, user.id, db)
    for page in pages:
        await socket_manager.emit("dispatch", page)

    return {"message": "Dispatched", "request id": request_id}


@sync_router.get("/dispatch/all")
def dispatch_all(
    user: User = Depends(get_current_user),
    db=Depends(get_db),
):

    cids = get_user_cids(user.id, db)
    queried_bytes = get_collective_bytes(user.id, db)

    # # paginate and dispatch the files through the socketio connection
    pages = paginate_using_gb(queried_bytes, user.id, db)
    # for page in pages:
    #     socket_manager.emit("dispatch", page)

    return {
        "message": "Dispatched",
        "cids": cids,
        "bytes": queried_bytes,
        "pages": {"paginate": pages},
    }
