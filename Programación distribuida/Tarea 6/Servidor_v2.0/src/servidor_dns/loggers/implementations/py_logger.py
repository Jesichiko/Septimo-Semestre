import os
from ..interfaces.logger import BasicLogger
from ..interfaces.time_provider import TimeProvider
from ..interfaces.file_writer import FileWriter
from ..interfaces.directory_manager import DirectoryManager
from .system_time_provider import SystemTimeProvider
from .system_file_writer import SystemFileWriter
from .system_directory_manager import SystemDirectoryManager


class Logger(BasicLogger):

    def __init__(
        self,
        log_dir: str = "logs",
        time_provider: TimeProvider = None,
        file_writer: FileWriter = None,
        directory_manager: DirectoryManager = None,
    ):
        self.log_dir = log_dir
        self.time_provider = time_provider or SystemTimeProvider()
        self.file_writer = file_writer or SystemFileWriter()
        self.directory_manager = directory_manager or SystemDirectoryManager()

    def log(self, level: str, message: str, filename: str = "app.log") -> None:
        self.directory_manager.ensure_directory_exists(self.log_dir)

        timestamp = self.time_provider.now()

        log_entry = f"[{timestamp}] [{level}] {message}\n"
        filepath = os.path.join(self.log_dir, filename)
        self.file_writer.write(filepath, log_entry)
