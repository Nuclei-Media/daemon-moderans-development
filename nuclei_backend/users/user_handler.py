from fastapi import Depends, HTTPException

from . import user_handler_utils
from .auth_utils import *
from .main import users_router
from .auth_utils import authenticate_user, create_access_token, get_current_user
from ..users.auth_utils import get_current_user
from ..users.user_handler_utils import get_db, get_user


@users_router.post("/register", response_model=user_handler_utils.user_schemas.User)
def create_user(
    user: user_handler_utils.user_schemas.UserCreate,
    db: user_handler_utils.Session = Depends(user_handler_utils.get_db),
):
    if user_handler_utils.get_user_by_username(db, username=user.username):
        raise HTTPException(
            status_code=401, detail="User with this email already exists"
        )
    user_handler_utils.create_user(db=db, user=user)
    return status.HTTP_200_OK


@users_router.post("/add_friend")
async def add_friend(
    user: User = Depends(get_current_user),
    db=Depends(get_db),
):
    ...
