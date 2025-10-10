from typing import Protocol


class BasicLogger(Protocol):
    def log(self, level: str, message: str, filename: str) -> None: ...
