"""El mensaje que emita un server tendra dos caminos:
1. Respuesta o Peticion a Server
2. Respuesta o Mensaje a un Cliente

Para unificar la estructura de
estos dos tipos de mensajes, usaremos un
formato JSON estandarizado en nuestro sistema,
el cual es:

{
    "type_request": "peticion" | "respuesta",
    "status": "ACK" | "NACK",
    "authority": "autoritativo" | "no_autoritativo",
    "files": [
        "docu1.txt",
        "docu2.txt",
        "docu3.txt"
    ],
}"""

import json


class Message:
    def __init__(
        self,
        type_request: str,
        target: str,
        status: str,
        authority: str,
        files: list[str],
        ip: str
    ):
        self.type_request = type_request
        self.target = target
        self.status = status
        self.authority = authority
        self.files = files or []
        self.ip = ip

    @property
    def dictionary(self):
        return {
            "type": self.type_request,
            "target": self.target,
            "status": self.status,
            "authority": self.authority,
            "files": self.files,
        }

    @property
    def json(self):
        return json.dumps(self.dictionary, indent=2)
