from ..interfaces.file_writer import FileWriter


class PyFileWriter(FileWriter):
    def write(self, filepath: str, content: str) -> None:
        try:
            with open(filepath, "a", encoding="utf-8") as file:
                file.write(content)
        except Exception as e:
            raise ValueError(e)
