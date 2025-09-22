from typing import Optional

from RequestDeliver import RequestDeliver as deliver

from ..data.Message import Message
from ..services.sync.Files import Files
from ..services.transfer.FileTransfer import FileTransfer


class RequestProcessor:

    def __init__(self, ip: str, database_dir: str, files_manager: Files):
        self.servers = []
        self.ip = ip
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
            "ip" : "192.0.128.0...:8080" (del dueño),
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
            target="client",
            status="NACK",
            authority="no_autoritativo",
            files=files,
            ip=self.ip,
        )

    def _search_file_in_network(self, filename: str) -> Message:
        # TO DO

        for servers in self.servers:
            # Enviamos peticion
            deliver.send_response(
                Message(
                    type_request="peticion",
                    target="server",
                    status="",
                    authority="",
                    files=filename,
                    ip=self.ip,
                )
            )

            # Escuchamos respuesta (TO DO)
            response = "i dont knowwwwwwwww"

            # Verificamos respuesta
            if response["status"] == "ACK":
                if response["authority"] == "autoritativo":
                    pass  # recibimos la copia
                else:  # enviamos al propio dueño la request
                    deliver.send_response(
                        Message(
                            type_request="peticion",
                            target="server",
                            status="",
                            authority="",
                            files=filename,
                            ip=response["ip"],
                        )
                    )

        return self._create_not_found_response([filename])

    def _file_exists_locally(self, filename: str) -> bool:
        content = self.file_transfer.read_file_content(filename)
        return content is not None

    def get_file_content(self, filename: str) -> Optional[bytes]:
        return self.file_transfer.read_file_content(filename)
