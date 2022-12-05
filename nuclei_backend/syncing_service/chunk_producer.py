import hashlib
import math
import os


class ChunkProducer:
    def __init__(self, file_path, chunk_size=1024):
        self.file_path = file_path
        self.chunk_size = chunk_size
        self.file_size = os.path.getsize(file_path)
        self.chunk_count = math.ceil(self.file_size / self.chunk_size)
        self.file_name = os.path.basename(file_path)
        self.file_extension = os.path.splitext(file_path)[1]
        self.file_hash = self.get_file_hash()
        self.chunk_hashes = self.get_chunk_hashes()

    def get_file_hash(self):
        return hashlib.sha256(open(self.file_path, "rb").read()).hexdigest()

    def get_chunk_hashes(self):
        chunk_hashes = []
        with open(self.file_path, "rb") as f:
            chunk_hashes.extend(
                hashlib.sha256(chunk).hexdigest()
                for chunk in iter(lambda: f.read(self.chunk_size), b"")
            )

        return chunk_hashes

    def get_chunk(self, chunk_index):
        with open(self.file_path, "rb") as f:
            f.seek(chunk_index * self.chunk_size)
            return f.read(self.chunk_size)

    def get_chunk_hash(self, chunk_index):
        return self.chunk_hashes[chunk_index]

    def get_chunk_count(self):
        return self.chunk_count

    def get_file_name(self):
        return self.file_name

    def get_file_extension(self):
        return self.file_extension

    def get_file_hash(self):
        return self.file_hash

    def get_file_size(self):
        return self.file_size
