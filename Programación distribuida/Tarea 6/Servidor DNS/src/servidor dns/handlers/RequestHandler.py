from typing import Tuple

from ..data.Message import Message
from .RequestProcessor import RequestProcessor


class RequestHandler:

    def __init__(self, processor: RequestProcessor):
        self.processor = processor

    def handle_server_request(
        self, server_ip: str, server_id: str, filename: str
    ) -> Message:
        """Maneja peticion de otro servidor"""

        requester_info = {"type": "server", "address": server_ip, "id": server_id}
        return self.processor.process_file_request(requester_info, filename)

    def handle_client_request(
        self, client_addr: Tuple[str, int], filename: str
    ) -> Message:
        """Maneja petición de un cliente"""
        requester_info = {
            "type": "client",
            "address": client_addr,
            "id": f"client_{client_addr[0]}_{client_addr[1]}",
        }
        return self.processor.process_file_request(requester_info, filename)
