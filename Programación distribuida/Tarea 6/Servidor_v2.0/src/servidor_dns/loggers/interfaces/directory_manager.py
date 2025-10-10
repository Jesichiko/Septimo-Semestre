from typing import Protocol


class DirectoryManager(Protocol):
    def ensure_directory_exists(self, path: str) -> None: ...
