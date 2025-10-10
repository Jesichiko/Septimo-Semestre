from ..interfaces.directory_manager import DirectoryManager
import os


class PyDirectoryManager(DirectoryManager):
    def ensure_directory_exists(self, path: str) -> None:
        if not os.path.exists(path=path):
            os.makedirs(name=path)
