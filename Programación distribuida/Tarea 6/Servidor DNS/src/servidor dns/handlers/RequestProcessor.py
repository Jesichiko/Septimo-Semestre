from RequestDeliver import RequestDeliver as deliver

from ..data.Message import Message
from ..services.transfer.FileTransfer import FileTransfer as transfer


class RequestProcessor:

    def __init__(self, ip: str, server_list: set[str], file_list: set[str]) -> None:
        self.ip: int = ip
        self.servers: set[str] = server_list
        self.files: set[str] = file_list

        # Tuplas de archivo, dueño
        self.temporary_file_list: list[tuple[str, str]]

    def set_servers(self, new_servers: set[str]) -> None:
        self.servers = new_servers.copy()

    def set_files(self, new_serves: set[str]) -> None:
        self.files = new_serves.copy

    def _create_response(self, target: str, status: str, authority: str, files: list[str]) -> Message:
        return Message(
            type_request="respuesta",
            target=target,
            status=status,
            authority=authority,
            files=files,
            ip=self.ip,
        )

    def process_request(self, requester_info: dict) -> Message:
        if requester_info["type_request"]

    def process_file_request(self, requester_info: dict) -> Message:
        """
        este metodo es el principal, procesamos cualquier peticion
        que nos llegue del tipo

            "type_request": "peticion",
            "target:" "server" | "client"
            "files": "file.txt" | "all"
            "ip" : "192.0.128.0...:8080" (del dueño),

            Si pregunta otro servidor, enviamos:

            "type_request": respuesta",
            "target:" "server"
            "status": "ACK" | "NACK",
            "authority": "autoritativo" | "no_autoritativo",
            "files": [
                "docu1.txt",
                "docu2.txt",
                "docu3.txt"
            ],
            "ip" : "192.0.128.0...:8080" (del dueño),

            Si es un cliente, buscamos localmente y sino esta
            el archivo, buscamos en red
        """

        file_request = requester_info["files"]
        entity = requester_info["target"]

        # Verificamos si pide mas de un archivo

        # si es cliente, recolectamos los demas archivos de todos
        if file_request == "all":
            if
            return self.get_all_files()

        # Verificamos si tenemos el archivo localmente
        if self._file_exists_locally(filename):
            return self._create_success_response([filename], requester_info)

        # Si no lo tenemos y esta pidiendo cliente, buscamos en otros servers
        if requester_info["type"] == "client":
            return self._search_file_in_network(filename, requester_info)
        else:
            return self._create_not_found_response([filename])

    def get_all_files(self) -> Message:
        for

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
        return filename in self.files
