from fastapi import APIRouter
from .socket_connection import SocketManager, handle_connect

sync_router = APIRouter(prefix="/data/sync")

socket_manager = SocketManager()
socket_manager.on("connect", handler=handle_connect)

from .sync_service_endpoints import *
