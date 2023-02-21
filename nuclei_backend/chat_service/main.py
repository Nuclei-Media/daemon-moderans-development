from fastapi import APIRouter


chat_controller = APIRouter(prefix="/chat")

from .chat_endpoints import *
