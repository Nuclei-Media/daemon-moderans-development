from .user_quota_main import quota_router
from ..users.auth_utils import get_current_user
from ..users.user_handler_utils import get_db
from fastapi import Depends
from ..users.user_models import User
from .quota_utils import increase_quota, decrease_quota, get_current_quota
from ..syncing_service.sync_utils import get_collective_bytes


@quota_router.post("/increase")
def increase_endpoint(
    user: User = Depends(get_current_user),
    db=Depends(get_db),
    increase_amount=int,
    files_count=int,
):
    current_byte_amount = get_current_quota(user.id, db)
    if (current_byte_amount + increase_amount) == current_byte_amount:
        return {"error": "quota amount miss-match", "code": 401}
    else:
        try:
            increase_quota(user.id, db, increase_amount, files_count)
        except Exception as e:
            return {"error": e}


@quota_router.post("/decrease")
def decrease_endpoint(
    user: User = Depends(get_current_user),
    db=Depends(get_db),
    decrease_amount=int,
    files_count=int,
):
    current_byte_amount = get_current_quota(user.id, db)
    if (current_byte_amount + decrease_amount) == current_byte_amount:
        return {"error": "quota amount miss-match", "code": 401}
    else:
        try:
            decrease_quota(user.id, db, decrease_amount, files_count)
        except Exception as e:
            return {"error": e}


@quota_router.post("/update")
def update_quota_endpoint(
    user: User = Depends(get_current_user),
    db=Depends(get_db),
):
    current_quota = get_current_quota(user.id, db)
    current_byte_count = get_collective_bytes(user.id, db)

    return {"current quota": current_quota, "current byte count": current_byte_count}
