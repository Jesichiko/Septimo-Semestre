from abc import ABC, abstractmethod
from datetime import datetime
from typing import Protocol
import os
import json

# DIP: Abstracciones para las dependencias


class TimeProvider(Protocol):
    def now(self) -> str: ...


class FileWriter(Protocol):
    def write(self, filepath: str, content: str) -> None: ...


class DirectoryManager(Protocol):
    def ensure_directory_exists(self, path: str) -> None: ...


# Implementaciones concretas


class SystemTimeProvider:
    def now(self) -> str:
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


class SystemFileWriter:
    def write(self, filepath: str, content: str) -> None:
        try:
            with open(filepath, "a", encoding="utf-8") as file:
                file.write(content)
        except Exception as e:
            print(f"Error escribiendo archivo {filepath}: {e}")


class SystemDirectoryManager:
    def ensure_directory_exists(self, path: str) -> None:
        if not os.path.exists(path):
            os.makedirs(path)
            print(f"Directorio creado: {path}")


# ISP: Interface segregada para logging básico


class BasicLogger(ABC):
    @abstractmethod
    def log(self, level: str, message: str, filename: str = "app.log") -> None:
        pass


# SRP: Clase enfocada solo en el mecanismo de logging


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


# OCP: Extensión sin modificación - Formatters


class LogFormatter(ABC):
    @abstractmethod
    def format(self, level: str, message: str, timestamp: str, **kwargs) -> str:
        pass


class StandardFormatter(LogFormatter):
    def format(self, level: str, message: str, timestamp: str, **kwargs) -> str:
        return f"[{timestamp}] [{level}] {message}\n"


class JsonFormatter(LogFormatter):
    def format(self, level: str, message: str, timestamp: str, **kwargs) -> str:
        log_data = {
            "timestamp": timestamp,
            "level": level,
            "message": message,
            **kwargs,
        }
        return json.dumps(log_data) + "\n"


# OCP: Logger extensible con formatters


class FormattableLogger(BasicLogger):
    def __init__(
        self,
        log_dir: str = "logs",
        formatter: LogFormatter = None,
        time_provider: TimeProvider = None,
        file_writer: FileWriter = None,
        directory_manager: DirectoryManager = None,
    ):
        self.log_dir = log_dir
        self.formatter = formatter or StandardFormatter()
        self.time_provider = time_provider or SystemTimeProvider()
        self.file_writer = file_writer or SystemFileWriter()
        self.directory_manager = directory_manager or SystemDirectoryManager()

    def log(self, level: str, message: str, filename: str = "app.log") -> None:
        self.directory_manager.ensure_directory_exists(self.log_dir)
        timestamp = self.time_provider.now()
        log_entry = self.formatter.format(level, message, timestamp)
        filepath = os.path.join(self.log_dir, filename)
        self.file_writer.write(filepath, log_entry)


# SRP: Clases especializadas para diferentes dominios


class WarmfileLogger:
    def __init__(self, logger: BasicLogger):
        self.logger = logger

    def log_warmfile(self, files: set, ttl: int, action: str = "cargado") -> None:
        message = f"WARMFILE {action} - Archivos: {list(files)}, TTL: {ttl}s"
        self.logger.log("INFO", message, "warmfile.log")


class FilesSyncLogger:
    def __init__(self, logger: BasicLogger):
        self.logger = logger

    def log_files(self, files: set) -> None:
        message = (
            f"Archivos sincronizados - Cantidad: {len(files)}, Archivos: {list(files)}"
        )
        self.logger.log("INFO", message, "files.log")


class ServerLogger:
    def __init__(self, logger: BasicLogger):
        self.logger = logger

    def log_servers(self, servers: set) -> None:
        servers_list = list(servers) if servers else []
        message = f"Servers encontrados - Cantidad: {len(servers_list)}, Servers: {
            servers_list
        }"
        self.logger.log("INFO", message, "servers.log")

    def log_server_startup(self, ip: str, port: int, database: set) -> None:
        message = (
            f"Servidor Iniciado - IP: {ip}, Port: {port}, Database: {list(database)}"
        )
        self.logger.log("INFO", message, "server.log")

    def log_server_shutdown(self, files: set) -> None:
        message = f"Servidor Apagandose - Database: {list(files)}"
        self.logger.log("INFO", message, "server.log")


class TransferLogger:
    def __init__(self, logger: BasicLogger):
        self.logger = logger

    def log_transferred_files(
        self, filename: str, target_ip: str, success: bool = True
    ) -> None:
        status = "exitosa" if success else "fallida"
        level = "INFO" if success else "ERROR"
        message = f"Transferencia de archivos {status} - Archivo: {filename}, Target: {
            target_ip
        }"
        self.logger.log(level, message, "transfers.log")


class RequestLogger:
    def __init__(self, logger: BasicLogger):
        self.logger = logger

    def log_requests(
        self, request_type: str, target: str, files: list, source_ip: str
    ) -> None:
        message = f"Peticion procesada - Tipo: {request_type}, Target: {
            target
        }, Archivos: {files}, IP: {source_ip}"
        self.logger.log("INFO", message, "requests.log")


class ErrorLogger:
    def __init__(self, logger: BasicLogger):
        self.logger = logger

    def log_error(
        self, error_type: str, error_message: str, context: str = None
    ) -> None:
        context_info = f" - Contexto: {context}" if context else ""
        message = f"ERROR {error_type} - {error_message}{context_info}"
        self.logger.log("ERROR", message, "errors.log")


# Ejemplo de uso
if __name__ == "__main__":
    # Logger básico
    basic_logger = Logger()

    # Logger con formato JSON
    json_logger = FormattableLogger(formatter=JsonFormatter())

    # Loggers especializados
    warmfile_logger = WarmfileLogger(basic_logger)
    server_logger = ServerLogger(json_logger)
    error_logger = ErrorLogger(basic_logger)

    # Uso
    warmfile_logger.log_warmfile({"file1.txt", "file2.txt"}, 300, "cargado")
    server_logger.log_server_startup("192.168.1.1", 8080, {"db1", "db2"})
    error_logger.log_error("CONNECTION", "No se pudo conectar al servidor", "startup")
