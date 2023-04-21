from fastapi import APIRouter

subscription_service = APIRouter(prefix="/subscription")

from .subscription_service_routes import *
