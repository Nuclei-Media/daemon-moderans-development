import json
import redis
import time
import pathlib
from apscheduler.schedulers.background import BackgroundScheduler
from functools import lru_cache
from .scheduler_config import SchConfig

import base64


class RedisController:
    def __init__(self):
        self.redis_connection = redis.Redis().from_url(
            url="redis://default:redispw@localhost:6379", decode_responses=True
        )

    def set_files(self, user: id, file: list[dict[str, bytes]]):

        return self.redis_connection.set(str(user), str(file))

    def get_files(self, user: str):
        # get the list of files for a user
        return self.redis_connection.get(user)

    def clear_cache(self, user: str):
        return self.redis_connection.delete(user)

    def check_files(self, user: str):

        return self.redis_connection.exists(user)


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

    def check_scheduler(self):
        return self.scheduler.running

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
    def __init__(self, user_id, session_id):
        super().__init__()
        self.user_id = user_id
        self.redis = RedisController()
        self.session_id = session_id

    @lru_cache(maxsize=None)
    def file_listener(self):
        folder_path = self.path / str(self.session_id)
        print("folder path", folder_path)
        if folder_path.is_dir():
            time.sleep(2)
            files_index = open(f"{self.session_id}.internal.json", "r").read()
            data = json.loads(files_index)
            data = dict(data)
            data = data.items()
            dispatch_dict = {str(self.user_id): []}

            for _ in data:
                with open(_[0], "rb") as file_read_buffer:
                    file_read_buffer = file_read_buffer.read()

                dispatch_dict[str(self.user_id)].append(
                    {str(_[0]): base64.encodebytes(file_read_buffer).decode()}
                )
            # replace all ' with " in the dict
            dispatch_dict = str(dispatch_dict).replace("'", '"')
            # convert the dict to json
            self.redis_controller.set_files(self.user_id, dispatch_dict)
