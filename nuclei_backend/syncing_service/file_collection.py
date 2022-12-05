from ticketing import TicketCache
from chunk_producer import ChunkProducer
import os
import subprocess
import time
import math


def coroutine(func):
    def wrapper(*args, **kwargs):
        gen = func(*args, **kwargs)
        next(gen)
        return lambda *args, **kwargs: gen.send((args, kwargs))

    return wrapper


class FileCollectionProducer:
    def __init__(self, user: str, cids: list):
        self.ticket = TicketCache.create_ticket()
        self.user = user

    def get_ticket(self):
        return self.ticket

    def get_user(self):
        return self.user

    def begin_download(self, file_path, cid):
        if os.path.exists(file_path):
            ticket = self.ticket
            TicketCache.cache_ticket(ticket)
            subprocess.Popen(
                [
                    "ipget",
                    "get",
                    "-o",
                    f"{ticket}_{cid}",
                    f"ipfs://{cid}",
                ]
            )
            return ticket
        else:
            return None

    def chunk_separately(self, file_path, cid):
        if os.path.exists(file_path):
            chunk_producer = ChunkProducer(file_path)
            return chunk_producer.get_chunk_count(), chunk_producer.get_chunk_hashes()
        else:
            return None

    @coroutine
    def folder_recursive_chunking(
        self, folder_path, cids, chunk_size=1024, chunk_count=0, chunk_hashes=None
    ):
        if chunk_hashes is None:
            chunk_hashes = []
        if os.path.exists(folder_path):
            for file in os.listdir(folder_path):
                file_path = os.path.join(folder_path, file)
                if os.path.isfile(file_path):
                    chunk_producer = ChunkProducer(file_path)
                    chunk_count += chunk_producer.get_chunk_count()
                    chunk_hashes.extend(chunk_producer.get_chunk_hashes())
                else:
                    self.folder_recursive_chunking(
                        file_path, cids, chunk_size, chunk_count, chunk_hashes
                    )
            return chunk_count, chunk_hashes
        else:
            return None
