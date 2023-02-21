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

from .chat_model import ChatRoom, ChatMessage, ChatRoomMembership
from .main import chat_controller

from .chat_utils import *


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

        room = ChatRoom(name=chat_name, owner_id=user.id)
        db.add(room)
        db.flush()

        membership_list = [
            ChatRoomMembership(user_id=member_id, room_id=room.id)
            for member_id in members
        ]
        membership_list.append(
            ChatRoomMembership(user_id=user.id, room_id=room.id)
        )  # Add creator to membership list
        db.add_all(membership_list)
        db.commit()

    except Exception as e:
        raise HTTPException(400, "Users aren't correctly referenced") from e

    return {"message": "Chat room created successfully"}


@chat_controller.get("/users/rooms")
async def dispatch_all(
    background_tasks: BackgroundTasks,
    user: User = Depends(get_current_user),
    db=Depends(get_db),
):
    return {
        "rooms": [
            db.query(ChatRoom).filter_by(owner_id=user.id).all(),
            db.query(ChatRoomMembership).filter_by(user_id=user.id).all(),
        ]
    }


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
):
    await websocket.accept()
    await websocket.send_text("pong")


@chat_controller.websocket("/chat/ws")
async def chat_websocket(
    websocket: WebSocket,
):
    await websocket.accept()
    while True:
        data = await websocket.receive_text()
        print(data)
