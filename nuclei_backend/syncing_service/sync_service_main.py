from fastapi import APIRouter

from .utils.socket_connection import SocketManager

sync_router = APIRouter(prefix="/data/sync")

socket_manager = SocketManager()
socket_manager.on("connect", handler=lambda sid, environ: print("connect ", sid))

from .sync_service_endpoints import *
