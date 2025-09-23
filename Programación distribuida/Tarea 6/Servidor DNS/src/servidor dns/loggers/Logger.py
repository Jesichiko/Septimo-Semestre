import datetime
import os
from typing import List, Optional, Set


class Logger:
    def __init__(self, log_dir: str = "logs") -> None:
        self.log_dir = log_dir

    def _create_log_directory(self) -> None:
        if not os.path.exists(self.log_dir):
            os.makedirs(self.log_dir)
            print(f"Directorio de logs creado: {self.log_dir}")

    def _write_log(self, filename: str, message: str) -> None:
        self._create_log_directory()

        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_entry = f"[{timestamp}] {message}\n"
        log_path = os.path.join(self.log_dir, filename)

        try:
            with open(log_path, "a", encoding="utf-8") as log_file:
                log_file.write(log_entry)
        except Exception as e:
            print(f"Error escribiendo en log {filename}: {e}")

    def log_warmfile(self, files: Set[str], ttl: int, action: str = "cargado") -> None:
        message = f"WARMFILE {action} - Archivos: {list(files)}, TTL: {ttl}s"
        self._write_log("warmfile.log", message)

    def log_files(self, files: Set[str]) -> None:
        message = f"Archivos sincronizados - Cantidad: {
            len(files)}, Archivos: {list(files)}"
        self._write_log("files.log", message)

    def log_servers(self, servers: Set[str]) -> None:
        servers_list = list(servers) if servers else []
        message = f"Servers encontrados - Cantidad: {
            len(servers_list)}, Servers: {servers_list}"
        self._write_log("servers.log", message)

    def log_transferred_files(
        self,
        filename: str,
        target_ip: str,
        success: bool = True,
    ) -> None:
        status = "exitosa" if success else "fallida"
        message = f"Transferencia de archivos {
            status} - Archivo: {filename}, Target: {target_ip}"
        self._write_log("transfers.log", message)

    def log_requests(
        self,
        request_type: str,
        target: str,
        files: List[str],
        source_ip: str,
    ) -> None:
        message = f"Peticion procesada - Tipo: {request_type}, Target: {
            target}, Archivos: {files}, IP: {source_ip}"
        self._write_log("requests.log", message)

    def log_error(
        self, error_type: str, error_message: str, context: Optional[str] = None
    ) -> None:
        context_info = f" - Contexto: {context}" if context else ""
        message = f"ERROR {error_type} - {error_message}{context_info}"
        self._write_log("errors.log", message)

    def log_server_startup(self, ip: str, port: int, database: Set[str]) -> None:
        message = f"Servidor Iniciado - IP: {ip}, Port: {
            port}, Database: {list(database)}"
        self._write_log("server.log", message)

    def log_server_shutdown(self, files: Set[str]) -> None:
        message = f"Servidor Apagandose - Database: {list(files)}"
        self._write_log("server.log", message)
