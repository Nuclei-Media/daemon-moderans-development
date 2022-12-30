from fastapi import APIRouter

permanent_store_router = APIRouter(prefix="/storage")

from . import permanent_store_routes
