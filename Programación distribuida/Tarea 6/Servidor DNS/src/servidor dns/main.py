import sys
import threading
import time

from .loggers.Logger import Logger
from .services.cache.Warmfile import Warmfile
from .services.sync.Files import Files
from .services.sync.ServerIPs import ServerIPs


def rastreo(fileHandler: Files, ipHandler: ServerIPs, ttl: int, logger: Logger):
    while True:
        time.sleep(5)

        try:
            # --- Archivos ---
            if fileHandler.are_new_changes():
                fileHandler.sync_files(ttl)
                logger.log_files(fileHandler.get_filenames())

            # --- Servidores ---
            if ipHandler.are_new_changes():
                ipHandler.sync_changes()
                logger.log_servers(ipHandler.get_servers())
        except Exception as e:
            logger.log_error("RASTREO", str(e), "Hilo de rastreo")


def main():
    my_ip = "192.0.12..."
    my_port = "50000"

    # Argumentos: main.py Files/ Servers.json ttl
    if len(sys.argv) < 4:
        print("Uso: python main.py <directorio_files> <servers.json> <ttl_segundos>")
        exit(-1)

    dir_files = sys.argv[1]
    servers_config = sys.argv[2]
    ttl_seconds = int(sys.argv[3])
    # Logger
    logger = Logger()

    # Handlers
    fileHandler = Files(dir_files)
    ipHandler = ServerIPs(servers_config)

    try:
        # 1. Cargamos warmfile si existe
        warmfile_result = Warmfile.load_warmfile("warmfile.txt")
        if warmfile_result is not None:
            config_warmfile, ttl_from_cache = warmfile_result
            fileHandler.load_files(ttl_from_cache)
            logger.log_warmfile(
                config_warmfile, ttl_from_cache, "cargado desde cache")
        else:
            fileHandler.load_files(ttl_seconds)
            logger.log_files(fileHandler.get_filenames())

        # 2. Cargamos servidores (debe haber al menos uno)
        ipHandler.load_config_servers()
        logger.log_servers(ipHandler.get_servers())

        # 3. Creamos hilo de rastreo
        tracking_thread = threading.Thread(
            target=rastreo,
            args=(fileHandler, ipHandler, ttl_seconds, logger),
            daemon=True,
        )
        tracking_thread.start()

        logger.log_server_startup(my_ip, my_port, fileHandler.get_filenames())

        # 4. Empezar a escuchar peticiones (enviarlas y responderlas)

        # Mantener el programa corriendo
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            logger.log_server_shutdown(fileHandler.get_filenames())
            print("\nServidor detenido, adios! :)")

    except Exception as e:
        logger.log_error("STARTUP", str(e), "Inicializacion del servidor")
        raise
