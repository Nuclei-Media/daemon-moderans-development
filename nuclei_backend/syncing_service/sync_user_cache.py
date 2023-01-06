from typing import List
import redis
import time
import pathlib
import os
import sys
from apscheduler.schedulers.background import BackgroundScheduler
from uuid import uuid4
from functools import total_ordering, lru_cache


class RedisController:
    def __init__(self):
        self.redis_connection = redis.Redis(host="Localhost", port=6379, db=0)

    @lru_cache(maxsize=None)
    def initialise_user(self, user_id):
        self.redis_connection.expire(user_id, 86400)
        if self.redis_connection.ttl(user_id) == -1:
            self.redis_connection.delete(user_id)
        self.redis_connection.hset(user_id, "initialise", 1)

    @lru_cache(maxsize=None)
    def set_upload_user_files(self, user_id, files: List):
        for file in files:
            self.redis_connection.hset(user_id, file, 0)

    @lru_cache(maxsize=None)
    def serialize_user_files(self, user_id):
        return self.redis_connection.hgetall(user_id)


from .scheduler_config import SchConfig


class SchedulerController:
    def __init__(self):
        self.redis_controller = RedisController()
        self.scheduler = BackgroundScheduler(
            executors=SchConfig.executors,
            job_defaults=SchConfig.job_defaults,
            timezone=SchConfig.timezone,
        )
        self.path = pathlib.Path(__file__).parent.absolute() / "FILE_PLAYING_FIELD"

    @lru_cache(maxsize=None)
    def start_scheduler(self):
        self.scheduler.start()

    @lru_cache(maxsize=None)
    def add_job(self, job_id, func, trigger, **kwargs):
        self.scheduler.add_job(
            func=func,
            trigger=trigger,
            id=job_id,
            **kwargs,
        )
        self.scheduler.remove_job(job_id)


class FileListener(SchedulerController):
    def __init__(self, user_id):
        super().__init__()
        self.user_id = user_id
        self.redis = RedisController()

    @lru_cache(maxsize=None)
    def file_listener(self):
        try:
            for folders in os.listdir(self.path):

                folder_path = self.path / folders
                if folder_path.is_dir():
                    with open(folder_path / ".internal.txt", "r") as f:
                        user_id, file_names = f.read().split("\n")
                        file_names = file_names.split(",")
                        if self.redis_controller.redis_connection.exists(user_id):
                            for file in file_names:
                                self.redis.set_upload_user_files(user_id, file)
        except Exception as e:
            raise e from e

        return self.redis.serialize_user_files(self.user_id)

    @lru_cache(maxsize=None)
    def create_job(self, folder_uuid: str, user_id: str, file_names: List[str]):
        """
        It creates a job that runs every 10 seconds and calls the file_listener function with the
        user_id and file_names as arguments.

        Arguments:

        * `folder_uuid`: The unique identifier of the folder that the user is watching.
        * `user_id`: The user id of the user who uploaded the files
        * `file_names`: List[str]
        """
        try:
            self.add_job(
                job_id=folder_uuid,
                func=self.file_listener,
                trigger="interval",
                seconds=10,
                kwargs={"user_id": user_id, "file_names": file_names},
            )
        except Exception as e:
            raise e from e
