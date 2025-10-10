from typing import Protocol


class TimeProvider(Protocol):
    def time(self) -> str: ...
