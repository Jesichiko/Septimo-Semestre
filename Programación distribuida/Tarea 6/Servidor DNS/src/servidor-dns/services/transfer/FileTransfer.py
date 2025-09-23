import os


class FileTransfer:
    def read_file_content(self, filename: str, database_dir: str) -> bytes | None:
        filepath = os.path.join(database_dir, filename)
        if not os.path.exists(filepath):
            return None

        try:
            with open(filepath, "rb") as file:
                content = file.read()
                return content
        except (IOError, PermissionError) as e:
            print(f"Error: No se pudo leer archivo {filename}: {e}")
            return None
