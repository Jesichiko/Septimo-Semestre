from ..data.Message import Message
from .RequestProcessor import RequestProcessor

""" Handler para peticiones
Cuando una peticion llega primero:
    1. La recibe esta clase (Request Receiver)
    2. Se procesa la peticion (Request Processor)
    3. Se envia el mensaje final

    Es decir, el transcurso del proceso es:
        Receiver -> Processor ->  Receiver -> Sender

Cuando enviamos una peticion:
    1. Creamos primero la request a otro server sino tenemos el file
    2. Enviamos request

    Es decir, el transcurso de la request es:
        Create_Request -> search_file_in_network() -> Sender"""


class RequestHandler:

    def __init__(self, processor: RequestProcessor):
        self.processor = processor

    def handle_request() -> Message:
        # Manejamos primero la peticion, luego la enviamos

        pass

    # Procesa peticion de otro server
    def _handle_server_request() -> Message:
        pass

    # Procesa peticion de cliente
    def _handle_client_request() -> Message:
        pass
