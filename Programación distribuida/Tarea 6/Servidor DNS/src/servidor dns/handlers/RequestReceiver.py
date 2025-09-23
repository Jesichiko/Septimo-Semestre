import json
import threading

from ..loggers.Logger import Logger
from ..network.TCP.Connection import Connection


class RequestReceiver:
    """
    Responsabilidad: Escuchar y recibir peticiones entrantes
    - Maneja conexiones entrantes
    - Parsea mensajes JSON
    - Delega processing a RequestProcessor
    """

    def __init__(self, ip: str, port: int, processor, logger: Logger):
        self.ip = ip
        self.port = port
        self.processor = processor
        self.logger = logger
        self.connection = Connection(port, ip)
        self.running = False

    def start_listening(self):
        self.running = True
        listen_thread = threading.Thread(target=self._listen_loop, daemon=True)
        listen_thread.start()
        return listen_thread

    def stop_listening(self):
        self.running = False

    def _listen_loop(self):
        """Loop principal para escuchar peticiones"""
        print(f"🔊 Servidor escuchando en {self.ip}:{self.port}")

        while self.running:
            try:
                # Recibir mensaje
                data, client_address = self.connection.ReceiveFrom(4096)

                # Procesar en hilo separado para no bloquear
                processing_thread = threading.Thread(
                    target=self._handle_incoming_request,
                    args=(data, client_address),
                    daemon=True,
                )
                processing_thread.start()

            except Exception as e:
                if self.running:  # Solo log si no es shutdown intencional
                    self.logger.log_error("RECEIVER", f"Error recibiendo: {e}")

    def _handle_incoming_request(self, data: bytes, client_address: tuple):
        """Maneja una petición individual"""
        try:
            # Parsear JSON
            message_dict = json.loads(data.decode("utf-8"))

            # Log de la petición
            self.logger.log_requests(
                message_dict.get("type_request", "unknown"),
                message_dict.get("target", "unknown"),
                message_dict.get("files", []),
                f"{client_address[0]}:{client_address[1]}",
            )

            # Procesar petición
            response = self.processor.process_request(message_dict, client_address)

            # Enviar respuesta
            if response:
                response_data = response.json.encode("utf-8")
                self.connection.sendTo(response_data, client_address)

        except json.JSONDecodeError as e:
            self.logger.log_error(
                "RECEIVER",
                f"JSON inválido de {
                                  client_address}: {e}",
            )
        except Exception as e:
            self.logger.log_error("RECEIVER", f"Error procesando request: {e}")
