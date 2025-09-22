from ...data.File import File as file
from ..detection.Detection import Detection as detect


class Files:
    def __init__(self, name_dir: str) -> None:
        self.name_dir = name_dir
        self.loaded_files: set(str) = set()
        self.new_files: set(str) = set()
        self.files: set(file.File) = set()

    def get_filenames(self) -> set[str]:
        return self.loaded_files

    def load_files(self, ttl_seconds: int) -> set[file.File]:
        self.loaded_files = detect.Detection.detect(self.name_dir)
        if not self.loaded_files:
            raise ValueError("Error: No existe la carpeta ingresada")

        self.files = {file.File(file, ttl_seconds)
                      for file in self.loaded_files}
        return self.files

    def are_new_changes(self) -> bool:
        self.new_files = detect.Detection.detect(self.name_dir)
        if not self.new_files:
            raise ValueError("Error: No existe la carpeta ingresada")

        return self.loaded_files != self.new_files

    def sync_files(self, ttl_seconds: int) -> None:
        self.files = {file.File(file, ttl_seconds) for file in self.new_files}
        self.loaded_files = self.new_files.copy()
