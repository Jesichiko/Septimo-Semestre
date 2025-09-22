import os
from typing import Optional


class FileTransfer:

    def __init__(self, database_dir: str):
        self.database_dir = database_dir

    def read_file_content(self, filename: str) -> Optional[bytes]:
        filepath = os.path.join(self.database_dir, filename)
        if not os.path.exists(filepath):
            return None

        try:
            with open(filepath, "rb") as file:
                content = file.read()
                return content
        except (IOError, PermissionError) as e:
            print(f"Error: No se pudo leer archivo {filename}: {e}")
            return None
