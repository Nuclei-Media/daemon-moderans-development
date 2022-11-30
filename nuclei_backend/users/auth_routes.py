from datetime import timedelta

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm

from nuclei_backend.users import user_handler_utils

from typing import Optional
from fastapi.middleware.cors import CORSMiddleware
from starlette.requests import Request
from starlette.middleware.sessions import SessionMiddleware
import uvicorn

# import db
from .auth_utils import Token, authenticate_user, create_access_token, get_current_user
from .main import users_router
from .user_models import User

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/user/token")


@users_router.post("/token", response_model=Token)
def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db=Depends(user_handler_utils.get_db),
):
    """
    It takes a username and password, checks if the user exists, and if so, returns a token.

    Args:
      form_data (OAuth2PasswordRequestForm): OAuth2PasswordRequestForm = Depends()
      db: Depends(user_handler_utils.get_db)

    Returns:
      A token
    """

    user = authenticate_user(
        username=form_data.username,
        password=form_data.password,
        db=db,
    )
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=30)
    access_token = create_access_token(
        data={"sub": user.username},
        expire_delta=access_token_expires,
    )
    return {"access_token": access_token, "token_type": "bearer"}


@users_router.get("/me")
async def read_users_me(current_user: User = Depends(get_current_user)):
    """
    The function `read_users_me` is a FastAPI route handler that returns the current user

    Args:
      current_user (User): User = Depends(get_current_user)

    Returns:
      The current user.
    """
    return current_user
