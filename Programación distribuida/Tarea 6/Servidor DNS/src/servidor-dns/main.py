import sys
import threading
import time

from .handlers.RequestProcessor import RequestProcessor
from .handlers.RequestReceiver import RequestReceiver
from .handlers.RequestSender import RequestSender
from .loggers.Logger import Logger
from .services.cache.Warmfile import Warmfile
from .services.sync.Files import Files
from .services.sync.ServerIPs import ServerIPs


class DNSServer:
    """
    Servidor DNS distribuido completo
    Integra todos los componentes: sync, handlers, network, logging
    """

    def __init__(
        self,
        my_ip: str,
        client_port: int,
        server_port: int,
        dir_files: str,
        servers_config: str,
        ttl_seconds: int,
    ) -> None:
        self.my_ip = my_ip
        self.client_port = client_port
        self.server_port = server_port
        self.ttl_seconds = ttl_seconds

        # Componentes principales
        self.logger = Logger()
        self.fileHandler = Files(dir_files)
        self.ipHandler = ServerIPs(servers_config)

        # Handlers de red
        self.sender = RequestSender(self.logger)
        self.processor = RequestProcessor(my_ip, server_port, dir_files)
        self.receiver = RequestReceiver(
            my_ip, client_port, self.processor, self.logger)

        # Hilos
        self.tracking_thread = None
        self.server_thread = None
        self.running = False

    def initialize(self):
        """Inicializa todos los componentes del servidor"""
        try:
            # 1. Cargar warmfile si existe
            warmfile_result = Warmfile.load_warmfile("warmfile.txt")
            if warmfile_result is not None:
                config_warmfile, ttl_from_cache = warmfile_result
                self.fileHandler.load_files(ttl_from_cache)
                self.logger.log_warmfile(
                    config_warmfile, ttl_from_cache, "cargado desde cache"
                )
            else:
                self.fileHandler.load_files(self.ttl_seconds)
                self.logger.log_files(self.fileHandler.get_filenames())

            # 2. Cargar servidores
            self.ipHandler.load_config_servers()
            self.logger.log_servers(self.ipHandler.get_servers())

            # 3. Configurar dependencias del processor
            self.processor.set_dependencies(
                self.ipHandler.get_servers(),
                self.fileHandler.get_filenames(),
                self.sender,
                self.logger,
            )

            self.logger.log_server_startup(
                self.my_ip, self.client_port, self.fileHandler.get_filenames()
            )

            print("Servidor inicializado")
            print(f"Archivos: {list(self.fileHandler.get_filenames())}")
            print(f"Servidores: {list(self.ipHandler.get_servers())}")

        except Exception as e:
            self.logger.log_error("STARTUP", str(
                e), "Inicializacion del servidor")
            raise

    def start(self):
        """Inicia el servidor y todos sus hilos"""
        self.running = True

        # 1. Iniciar hilo de rastreo
        self.tracking_thread = threading.Thread(
            target=self._tracking_loop, daemon=True)
        self.tracking_thread.start()

        # 2. Iniciar servidor de peticiones
        self.server_thread = self.receiver.start_listening()

        print(f"Servidor DNS iniciado en {self.my_ip}:{self.client_port}")
        print(f"Puerto servidor: {self.server_port}")
        print(f"TTL: {self.ttl_seconds} segundos")

    def stop(self):
        """Detiene el servidor de manera limpia"""
        self.running = False
        self.receiver.stop_listening()

        # Guardar warmfile antes de salir
        try:
            warmfile = Warmfile()
            warmfile.save_warmfile(
                "warmfile.txt", self.fileHandler.get_filenames(), self.ttl_seconds
            )
            self.logger.log_warmfile(
                self.fileHandler.get_filenames(), self.ttl_seconds, "guardado en cache"
            )
        except Exception as e:
            self.logger.log_error("SHUTDOWN", f"Error guardando warmfile: {e}")

        self.logger.log_server_shutdown(self.fileHandler.get_filenames())
        print("\nServidor DNS detenido, finalizando programa...")

    def _tracking_loop(self):
        """Hilo para rastrear cambios en archivos y servidores"""
        while self.running:
            time.sleep(5)

            try:
                # Verificar cambios en archivos
                if self.fileHandler.are_new_changes():
                    self.fileHandler.sync_files(self.ttl_seconds)
                    new_files = self.fileHandler.get_filenames()

                    # Actualizar processor
                    self.processor.update_files(new_files)

                    self.logger.log_files(new_files)
                    print(f"Archivos actualizados: {list(new_files)}")

                # Verificar cambios en servidores
                if self.ipHandler.are_new_changes():
                    self.ipHandler.sync_changes()
                    new_servers = self.ipHandler.get_servers()

                    # Actualizar processor
                    self.processor.update_servers(new_servers)

                    self.logger.log_servers(new_servers)
                    print(f"Servidores actualizados: {list(new_servers)}")

            except Exception as e:
                self.logger.log_error("TRACKING", str(e), "Hilo de rastreo")

    def get_status(self):
        """Retorna el estado actual del servidor"""
        return {
            "running": self.running,
            "ip": self.my_ip,
            "client_port": self.client_port,
            "server_port": self.server_port,
            "files": list(self.fileHandler.get_filenames()),
            "servers": list(self.ipHandler.get_servers()),
            "ttl": self.ttl_seconds,
        }


def main():
    # Configuracion del servidor
    client_port = 50000  # Puerto para clientes
    server_port = 20000  # Puerto para servidores

    # Argumentos: main.py <directorio_files> <servers.json> <ttl_segundos>
    if len(sys.argv) < 5:
        print(
            "Uso: python main.py <directorio_files> <servers.json> <ttl_segundos> <static_ip>"
        )
        print("Ejemplo: python main.py database/ config/servers.json 300")
        exit(-1)

    dir_files = sys.argv[1]
    servers_config = sys.argv[2]
    ttl_seconds = int(sys.argv[3])
    my_ip = sys.argv[4]

    # Creamos y configuramos servidor
    dns_server = DNSServer(
        my_ip, client_port, server_port, dir_files, servers_config, ttl_seconds
    )

    try:
        # Inicializamos y arrancamos servidor
        dns_server.initialize()
        dns_server.start()

        # Mantenemos servidor corriendo
        print("Servidor corriendo... Presiona Ctrl+C para detener")
        print("Status del servidor:")
        status = dns_server.get_status()
        for key, value in status.items():
            print(f"   {key}: {value}")

        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print("Deteniendo servidor, finalizando programa...")
            dns_server.stop()

    except Exception as e:
        print(f"Error en server: {e}, finalizando programa...")
        dns_server.stop()
        exit(-1)


if __name__ == "__main__":
    main()
