import contextlib
import json
import time
import typing
import uuid
from functools import lru_cache
from typing import Union

from fastapi import (
    Cookie,
    Depends,
    FastAPI,
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
from .chat_model import ChatRooms
from .main import chat_controller


def get_all_users_rooms(user: User) -> list:
    return ChatRooms().query.filter_by(owner_id=user).all()


def validate_users(db, members):
    for user_id in members:
        user = get_user(db, user_id)
        if not user:
            raise HTTPException(400, "users aren't correctly referenced")


@chat_controller.post("/create")
async def dispatch_all(
    background_tasks: BackgroundTasks,
    user: User = Depends(get_current_user),
    db=Depends(get_db),
    members: list = None,
    chat_name: str = None,
):
    try:
        if user.id in members:
            raise HTTPException(400, "User cannot be a member of their own chat")
        if validate_users(db, members):
            new_room = ChatRooms(owner_id=user.id, members=members, room_name=chat_name)
            db.add(new_room)
            db.commit()
            db.refresh(new_room)

    except Exception as e:
        raise HTTPException(400, "users aren't correctly referenced") from e

    return status.HTTP_200_OK


@chat_controller.get("/users/rooms")
async def dispatch_all(
    background_tasks: BackgroundTasks,
    user: User = Depends(get_current_user),
    db=Depends(get_db),
):
    return db.query(ChatRooms).filter_by(owner_id=user.id).all()


async def get_cookie_or_token(
    websocket: WebSocket,
    session: Union[str, None] = Cookie(default=None),
    token: Union[str, None] = Query(default=None),
):
    if session is None and token is None:
        raise WebSocketException(code=status.WS_1008_POLICY_VIOLATION)
    return session or token


@chat_controller.post("/enter_chat")
async def dispatch_all(
    background_tasks: BackgroundTasks,
    user: User = Depends(get_current_user),
    db=Depends(get_db),
    chat_name: str = None,
):
    ...


@chat_controller.websocket("/chat/{chat_message}/ws")
async def chat_websocket(
    websocket: WebSocket,
    chat_id: str,
    q: Union[int, None] = None,
    cookie_or_token: str = Depends(get_cookie_or_token),
    user: User = Depends(get_current_user),
    db=Depends(get_db),
):
    await websocket.accept()
    while True:
        data = await websocket.receive_bytes()
        await websocket.send_text(
            f"Session cookie or query token value is: {cookie_or_token}"
        )
        if q is not None:
            await websocket.send_text(f"Query parameter q is: {q}")
        await websocket.send_text(
            f"Message Text was: {data}, for Message ID: {chat_id}"
        )


@chat_controller.websocket("/ping/ws")
async def chat_websocket(
    websocket: WebSocket,
    chat_id: str,
    q: Union[int, None] = None,
    cookie_or_token: str = Depends(get_cookie_or_token),
    user: User = Depends(get_current_user),
    db=Depends(get_db),
):
    await websocket.send_text("pong")
