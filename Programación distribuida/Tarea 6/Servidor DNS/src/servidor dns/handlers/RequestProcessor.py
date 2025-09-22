from typing import Optional

from ..data.Message import Message
from ..services.sync.Files import Files
from ..services.transfer.FileTransfer import FileTransfer


class RequestProcessor:

    def __init__(self, ip: str, database_dir: str, files_manager: Files):
        self.servers = []
        self.ip = ip
        self.file_transfer = FileTransfer(database_dir)
        self.files_manager = files_manager

    def process_file_request(self, requester_info: dict, filename: str) -> Message:
        """
        este metodo es el principal, procesamos cualquier peticion
        que nos llegue

            "type_request": "peticion" | "respuesta",
            "target:" "server" | "client"
            "status": "ACK" | "NACK",
            "authority": "autoritativo" | "no_autoritativo",
            "files": [
                "docu1.txt",
                "docu2.txt",
                "docu3.txt"
            ],
            "ip" : "192.0.128.0...:8080",
        """

        # Verificamos si tenemos el archivo localmente
        if self._file_exists_locally(filename):
            return self._create_success_response([filename], requester_info)

        # Si no lo tenemos y esta pidiendo cliente, buscamos en otros servers
        if requester_info["type"] == "client":
            return self._search_file_in_network(filename, requester_info)
        else:
            return self._create_not_found_response([filename])

    def _create_success_response(self, target: str, files: list[str]) -> Message:
        return Message(
            type_request="respuesta",
            target=target,
            status="ACK",
            authority="autoritativo",
            files=files,
            ip=self.ip,
        )

    def _create_not_found_response(self, files: list[str]) -> Message:
        return Message(
            type_request="respuesta",
            status="NACK",
            authority="no_autoritativo",
            files=files,
            ip=self.ip,
        )

    def _search_file_in_network(self, filename: str, requester_info: dict) -> Message:
        # TO DO
        return self._create_not_found_response(filename)

    def _file_exists_locally(self, filename: str) -> bool:
        content = self.file_transfer.read_file_content(filename)
        return content is not None

    def get_file_content(self, filename: str) -> Optional[bytes]:
        return self.file_transfer.read_file_content(filename)
