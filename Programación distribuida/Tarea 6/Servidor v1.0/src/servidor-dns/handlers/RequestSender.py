import json
import socket
import time
from typing import Optional

from ..data.Message import Message
from ..loggers.Logger import Logger


class RequestSender:
    """
    Responsabilidad: Enviar peticiones a otros servidores
    - Crea conexiones salientes
    - Maneja timeouts y reintentos
    - Parsea respuestas
    """

    def __init__(self, logger: Logger, timeout: int = 5, max_retries: int = 2):
        self.logger = logger
        self.timeout = timeout
        self.max_retries = max_retries

    def send_request_to_server(
        self, message: Message, target_ip: str, target_port: int
    ) -> Optional[dict]:
        """
        Envía una petición a otro servidor y espera respuesta

        Returns:
            dict: Respuesta del servidor o None si falló
        """
        for attempt in range(self.max_retries + 1):
            try:
                # Crear socket para esta petición
                sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                sock.settimeout(self.timeout)

                # Enviar mensaje
                message_data = message.json.encode("utf-8")
                sock.sendto(message_data, (target_ip, target_port))

                # Esperar respuesta
                response_data, _ = sock.recvfrom(4096)
                response_dict = json.loads(response_data.decode("utf-8"))

                sock.close()
                return response_dict

            except socket.timeout:
                self.logger.log_error(
                    "SENDER",
                    f"Timeout enviando a {target_ip}:{
                                      target_port} (intento {attempt + 1})",
                )

            except json.JSONDecodeError as e:
                self.logger.log_error(
                    "SENDER",
                    f"Respuesta JSON inválida de {
                                      target_ip}:{target_port}: {e}",
                )
                break  # No reintentar en errores de formato

            except Exception as e:
                self.logger.log_error(
                    "SENDER",
                    f"Error enviando a {
                                      target_ip}:{target_port}: {e}",
                )

            finally:
                sock.close()

            # Esperar antes del siguiente intento
            if attempt < self.max_retries:
                time.sleep(0.5 * (attempt + 1))  # Backoff incremental

        return None

    def send_request_to_client(self, message: Message, client_address: tuple) -> bool:
        """
        Envía una respuesta a un cliente (no espera respuesta)

        Returns:
            bool: True si se envió exitosamente
        """
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            sock.settimeout(self.timeout)

            message_data = message.json.encode("utf-8")
            sock.sendto(message_data, client_address)

            sock.close()
            return True

        except Exception as e:
            self.logger.log_error(
                "SENDER",
                f"Error enviando a cliente {
                                  client_address}: {e}",
            )
            return False

    def broadcast_to_servers(
        self, message: Message, server_list: set[str], port: int
    ) -> dict:
        """
        Envía un mensaje a múltiples servidores

        Returns:
            dict: {server_ip: response_dict} para respuestas exitosas
        """
        responses = {}

        for server_ip in server_list:
            if server_ip != message.ip.split(":")[0]:  # No enviarse a sí mismo
                response = self.send_request_to_server(message, server_ip, port)
                if response:
                    responses[server_ip] = response

        return responses
