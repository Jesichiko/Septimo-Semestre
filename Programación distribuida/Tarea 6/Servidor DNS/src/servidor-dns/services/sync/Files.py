from ...data.File import File
from ..detection.Detection import Detection


class Files:
    def __init__(self, name_dir: str) -> None:
        self.name_dir = name_dir
        self.loaded_files: set[str] = set()
        self.new_files: set[str] = set()
        self.files: set[File] = set()

    def get_filenames(self) -> set[str]:
        return self.loaded_files

    def load_files(self, ttl_seconds: int) -> set[File]:
        detected_files = Detection.detect(self.name_dir)
        if detected_files is None:
            raise ValueError("Error: No existe la carpeta ingresada")

        # puede no haber archivos (osea [], forma parte de los casos posibles)
        self.loaded_files = detected_files
        self.files = {File(filename, ttl_seconds)
                      for filename in self.loaded_files}
        return self.files

    def are_new_changes(self) -> bool:
        self.new_files = Detection.detect(self.name_dir)
        if self.new_files is None:
            raise ValueError("Error: No existe la carpeta ingresada")

        return self.loaded_files != self.new_files

    def sync_files(self, ttl_seconds: int) -> None:
        if self.new_files is not None:
            self.files = {File(filename, ttl_seconds)
                          for filename in self.new_files}
            self.loaded_files = self.new_files.copy()
