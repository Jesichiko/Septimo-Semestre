from typing import List, Optional, Set

from ..data.Message import Message
from ..loggers.Logger import Logger
from ..services.transfer.FileTransfer import FileTransfer


class RequestProcessor:
    """
    Responsabilidad: Procesar la lógica de negocio de las peticiones
    - Decide qué hacer con cada tipo de petición
    - Maneja búsqueda local y en red
    - Coordina transferencia de archivos
    """

    def __init__(self, my_ip: str, server_port: int, database_dir: str):
        self.my_ip = my_ip
        self.server_port = server_port
        self.database_dir = database_dir
        self.file_transfer = FileTransfer()

        # Serán inyectados desde main
        self.servers: Set[str] = set()
        self.files: Set[str] = set()
        self.sender = None  # RequestSender inyectado
        self.logger = None  # Logger inyectado

    def set_dependencies(
        self, servers: Set[str], files: Set[str], sender, logger: Logger
    ):
        """Inyección de dependencias desde main"""
        self.servers = servers
        self.files = files
        self.sender = sender
        self.logger = logger

    def process_request(
        self, request_dict: dict, client_address: tuple
    ) -> Optional[Message]:
        """
        Punto de entrada principal para procesar peticiones
        """
        try:
            request_type = request_dict.get("type_request")
            target = request_dict.get("target")

            if request_type == "peticion":
                if target == "server":
                    return self._handle_server_request(request_dict, client_address)
                elif target == "client":
                    return self._handle_client_request(request_dict, client_address)

            return self._create_error_response("Tipo de petición no válido")

        except Exception as e:
            self.logger.log_error("PROCESSOR", f"Error procesando petición: {e}")
            return self._create_error_response("Error interno del servidor")

    def _handle_server_request(self, request: dict, client_address: tuple) -> Message:
        """
        Maneja peticiones de otros servidores
        Solo responde con archivos que tiene localmente
        """
        requested_files = request.get("files", [])
        if isinstance(requested_files, str):
            requested_files = [requested_files]

        # Buscar archivos localmente
        found_files = []
        for filename in requested_files:
            if filename in self.files:
                found_files.append(filename)

        if found_files:
            return Message(
                type_request="respuesta",
                target="server",
                status="ACK",
                authority="autoritativo",  # Tenemos el archivo original
                files=found_files,
                ip=f"{self.my_ip}:{self.server_port}",
            )
        else:
            return Message(
                type_request="respuesta",
                target="server",
                status="NACK",
                authority="no_autoritativo",
                files=[],
                ip=f"{self.my_ip}:{self.server_port}",
            )

    def _handle_client_request(self, request: dict, client_address: tuple) -> Message:
        """
        Maneja peticiones de clientes
        Busca localmente, y si no encuentra, busca en la red
        """
        requested_files = request.get("files", [])
        if isinstance(requested_files, str):
            if requested_files == "all":
                return self._handle_all_files_request()
            requested_files = [requested_files]

        found_files = []
        missing_files = []

        # 1. Buscar localmente
        for filename in requested_files:
            if filename in self.files:
                found_files.append(filename)
            else:
                missing_files.append(filename)

        # 2. Buscar archivos faltantes en la red
        if missing_files:
            network_files = self._search_files_in_network(missing_files)
            found_files.extend(network_files)

        if found_files:
            return Message(
                type_request="respuesta",
                target="client",
                status="ACK",
                authority="autoritativo",
                files=found_files,
                ip=f"{self.my_ip}:{self.server_port}",
            )
        else:
            return Message(
                type_request="respuesta",
                target="client",
                status="NACK",
                authority="no_autoritativo",
                files=[],
                ip=f"{self.my_ip}:{self.server_port}",
            )

    def _handle_all_files_request(self) -> Message:
        """
        Maneja petición de todos los archivos del sistema distribuido
        """
        all_files = set(self.files)  # Empezar con archivos locales

        # Pedir a todos los servidores sus archivos
        request_message = Message(
            type_request="peticion",
            target="server",
            status="",
            authority="",
            files=["all_local"],  # Petición especial para listar archivos
            ip=f"{self.my_ip}:{self.server_port}",
        )

        if self.sender:
            responses = self.sender.broadcast_to_servers(
                request_message, self.servers, self.server_port
            )

            # Recopilar archivos de las respuestas
            for server_ip, response in responses.items():
                if response.get("status") == "ACK":
                    server_files = response.get("files", [])
                    all_files.update(server_files)

        return Message(
            type_request="respuesta",
            target="client",
            status="ACK",
            authority="autoritativo",
            files=list(all_files),
            ip=f"{self.my_ip}:{self.server_port}",
        )

    def _search_files_in_network(self, filenames: List[str]) -> List[str]:
        """
        Busca archivos en otros servidores de la red
        """
        found_files = []

        if not self.sender:
            return found_files

        for filename in filenames:
            # Crear petición para este archivo
            request_message = Message(
                type_request="peticion",
                target="server",
                status="",
                authority="",
                files=[filename],
                ip=f"{self.my_ip}:{self.server_port}",
            )

            # Enviar a todos los servidores
            responses = self.sender.broadcast_to_servers(
                request_message, self.servers, self.server_port
            )

            # Buscar respuesta positiva
            for server_ip, response in responses.items():
                if response.get("status") == "ACK" and filename in response.get(
                    "files", []
                ):
                    found_files.append(filename)

                    # Log del archivo encontrado en red
                    self.logger.log_transferred_files(filename, server_ip, success=True)
                    break

        return found_files

    def _create_error_response(self, error_msg: str) -> Message:
        """Crea una respuesta de error estándar"""
        return Message(
            type_request="respuesta",
            target="client",
            status="NACK",
            authority="no_autoritativo",
            files=[],
            ip=f"{self.my_ip}:{self.server_port}",
        )

    def update_servers(self, new_servers: Set[str]):
        """Actualiza la lista de servidores"""
        self.servers = new_servers.copy()

    def update_files(self, new_files: Set[str]):
        """Actualiza la lista de archivos locales"""
        self.files = new_files.copy()
