from ..network.TCP.Connection import Connection


class ResponseSender:

    def __init__(self, connection: Connection, processor: RequestProcessor):
        self.connection = connection
        self.processor = processor

    def send_response(self, message: Message, requester_info: dict) -> bool:

        if message.status == "NACK":
            return self._send_error_response(message, requester_info)

        # Si tenemos el archivo, enviarlo
        if message.files:
            filename = message.files[0]
            content = self.processor.get_file_content(filename)

            if content:
                return self._send_file_content(content, filename, requester_info)

        return False

    def _send_error_response(self, message: Message, requester_info: dict) -> bool:
        """Envia mensaje de error"""
        response_data = message.json.encode()

        
        return True

    def _send_file_content(
        self, content: bytes, filename: str, requester_info: dict
    ) -> bool:
        """Envía el contenido del archivo"""
        # Aquí implementarías el protocolo específico para enviar archivos
        # Podría ser: mensaje JSON + contenido del archivo

        if requester_info["type"] == "server":
            return self._send_to_server(content, filename, requester_info["address"])
        else:
            return self._send_to_client(content, filename, requester_info["address"])

    def _send_to_server(self, content: bytes, filename: str, server_addr) -> bool:
        """Protocolo específico para enviar a servidores"""
        # Implementar protocolo servidor-servidor
        pass

    def _send_to_client(self, content: bytes, filename: str, client_addr) -> bool:
        """Protocolo específico para enviar a clientes"""
        # Implementar protocolo servidor-cliente
        2pass
