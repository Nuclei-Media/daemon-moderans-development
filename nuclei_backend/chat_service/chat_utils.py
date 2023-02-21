import contextlib
import json
import time
import typing
import uuid
from functools import lru_cache
from typing import Union

from fastapi import (
    Cookie,
    Query,
    WebSocket,
    WebSocketException,
    status,
)
from fastapi.background import BackgroundTasks
from fastapi_utils.tasks import repeat_every
from starlette.exceptions import HTTPException

from ..storage_service.ipfs_model import DataStorage
from ..users.auth_utils import get_current_user
from ..users.user_handler_utils import get_db, get_user
from ..users.user_models import User

from .chat_model import ChatRoom, ChatMessage, ChatRoomMembership
from .main import chat_controller

from .chat_utils import *


def get_all_users_rooms(user: User) -> list:
    return ChatRoom().query.filter_by(owner_id=user).all()


def validate_users(db, members):
    for user_id in members:
        user = get_user(db, user_id)
        if not user:
            raise HTTPException(400, "users aren't correctly referenced")


async def get_cookie_or_token(
    websocket: WebSocket,
    session: Union[str, None] = Cookie(default=None),
    token: Union[str, None] = Query(default=None),
):
    if session is None and token is None:
        raise WebSocketException(code=status.WS_1008_POLICY_VIOLATION)
    return session or token
