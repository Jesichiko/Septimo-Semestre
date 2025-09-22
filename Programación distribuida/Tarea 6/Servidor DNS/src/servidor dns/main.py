import sys
import threading
import time

import loggers.Logger as log
import services.cache.Warmfile as cache
import services.sync.Files as files
import services.sync.ServerIPs as server


def rastreo(fileHandler: files.Files, ipHandler: server.ServerIPs, ttl: int):
    while True:
        time.sleep(5)

        # --- Archivos ---
        if fileHandler.are_new_changes():
            fileHandler.sync_files(ttl)
            log.Logger.log_files(fileHandler.get_filenames)
        # --- Servidores ---
        if ipHandler.are_new_changes():
            ipHandler.sync_changes()
            log.Logger.log_servers(ipHandler.get_servers)


def main():
    # Argumentos: main.py Files/ Servers.json ttl

    if len(sys.argv) < 4:
        print("Uso: python main.py <directorio_files> <servers.json> <ttl_segundos>")
        exit(-1)

    dir_files = sys.argv[1]
    servers_config = sys.argv[2]
    ttl_seconds = int(sys.argv[3])

    # Handlers
    fileHandler = files.Files(dir_files)
    ipHandler = server.ServerIPs(servers_config)

    # 1. Cargamos warmfile si existe
    config_warmfile, ttl_from_cache = cache.Warmfile.load_warmfile(
        "warmfile.txt")
    if config_warmfile is not None:
        fileHandler.load_files(ttl_from_cache)
    else:
        fileHandler.load_files(ttl_seconds)

    # 2. Cargamos servidores (debe haber al menos uno)
    ipHandler.load_config_servers()

    # 3. Creamos hilo de rastreo
    tracking_thread = threading.Thread(
        target=rastreo, args=(fileHandler, ipHandler, ttl_seconds), daemon=True
    )
    tracking_thread.start()

    # 4. Empezamos a escuchar peticiones (y responderlas) como evento
