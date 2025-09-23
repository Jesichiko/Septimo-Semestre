import time


class File:
    def __init__(self, name: str, ttl_seconds: int):
        self.name = name
        self.ttl = ttl_seconds
        self.timestamp = time.time()

    def is_expired(self) -> bool:
        return (time.time() - self.timestamp) > self.ttl

    def get_name(self) -> str:
        return self.name

    def set_ttl(self, ttl_seconds: int):
        self.ttl = ttl_seconds
