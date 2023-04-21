from fastapi import APIRouter
import redis
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.schedulers.asyncio import AsyncIOScheduler


sync_router = APIRouter(prefix="/data/sync")
sched = BackgroundScheduler()
async_scheduler = AsyncIOScheduler()
redis_connection = redis.Redis(host="localhost", port=6379, db=0)


from .sync_service_endpoints import *
