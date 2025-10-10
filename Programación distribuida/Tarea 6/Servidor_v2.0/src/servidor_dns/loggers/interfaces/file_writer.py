from typing import Protocol


class FileWriter(Protocol):
    def write(self, filepath: str, content: str) -> None: ...
