import json
import logging
import socket
import sys
import threading
import time
from os import listdir
from os.path import exists, isfile, join

# Variable global para la lista de archivos (protegida por lock)
archivos_disponibles = []
archivos_lock = threading.Lock()

# Configuracion del servidor - definida explicitamente
UDP_IP = "127.0.0.1"
UDP_PORT = 50000

# Setup basico de logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(message)s",
    handlers=[
        logging.FileHandler("cambios_archivos.log", encoding="utf-8"),
        logging.StreamHandler(),
    ],
)


class ArchivoInfo:
    def __init__(self, nombre, ttl_seconds):
        self.nombre = nombre
        partes = nombre.split(".")
        self.extension = partes[-1] if len(partes) > 1 else ""
        self.ttl = ttl_seconds
        self.timestamp = time.time()

    def esta_expirado(self):
        return (time.time() - self.timestamp) > self.ttl


def cargar_warm_file(nombre_warm: str) -> list:
    archivos = []
    try:
        with open(nombre_warm, "r", encoding="utf-8") as f:
            for linea in f:
                partes = linea.strip().split()
                if len(partes) >= 2:
                    nombre = partes[0]
                    ttl = int(partes[1])
                    archivo_info = ArchivoInfo(nombre, ttl)
                    archivos.append(archivo_info)
    except Exception as e:
        print(f"Error cargando warm_file: {e}")
    return archivos


def guardar_warm_file(nombre_warm: str, archivos: list):
    try:
        with open(nombre_warm, "w", encoding="utf-8") as f:
            for i, archivo in enumerate(archivos):
                f.write(f"{archivo.nombre} {archivo.ttl} {i}\n")
    except Exception as e:
        print(f"Error guardando warm_file: {e}")


def leer_nombres_a_saltar(archivo_ignorar: str) -> list[str]:
    try:
        with open(archivo_ignorar, "r", encoding="utf-8") as f:
            return [line.strip() for line in f if line.strip()]
    except FileNotFoundError:
        print(
            f"Advertencia: No se encontro {
                archivo_ignorar}, no se ignorara nada"
        )
        return []


def leer_archivos(carpeta: str, nombres_a_saltar: list[str], ttl_segundos: int):
    archivos = []
    for archivo in sorted(listdir(carpeta)):
        if archivo in nombres_a_saltar:
            continue
        ruta = join(carpeta, archivo)
        if isfile(ruta):
            archivos.append(ArchivoInfo(archivo, ttl_segundos))
    return archivos


def existe_archivo(nombre_archivo: str, archivos_existentes: list) -> bool:
    for archivo in archivos_existentes:
        if archivo.nombre == nombre_archivo:
            return not archivo.esta_expirado()
    return False


def detectar_cambios(archivos_anteriores, archivos_nuevos):
    nombres_anteriores = {a.nombre for a in archivos_anteriores}
    nombres_nuevos = {a.nombre for a in archivos_nuevos}

    agregados = nombres_nuevos - nombres_anteriores
    eliminados = nombres_anteriores - nombres_nuevos

    if agregados:
        logging.info(f"Archivos agregados: {list(agregados)}")
    if eliminados:
        logging.info(f"Archivos eliminados: {list(eliminados)}")


def actualizar_archivos(
    carpeta: str,
    nombres_a_saltar: list,
    ttl_segundos: int,
    warm_file: str,
):
    global archivos_disponibles
    while True:
        try:
            time.sleep(10)

            archivos_anteriores = archivos_disponibles.copy()
            nuevos_archivos = leer_archivos(carpeta, nombres_a_saltar, ttl_segundos)

            with archivos_lock:
                archivos_disponibles = nuevos_archivos
                detectar_cambios(archivos_anteriores, nuevos_archivos)

                guardar_warm_file(warm_file, archivos_disponibles)

                print(
                    f"Lista de archivos actualizada: {
                        len(archivos_disponibles)} archivos encontrados"
                )

        except Exception as e:
            print(f"Error actualizando archivos: {e}")


def peticion_recibida(data: bytes) -> dict:
    try:
        return json.loads(data.decode("utf-8"))
    except json.JSONDecodeError as e:
        print(f"Error decodificando JSON: {e}")
        return {}


def crear_respuesta(peticion: dict, archivos_existentes: list) -> bytes:
    respuesta = {"operacion": "respuesta", "respuesta": "", "archivo": ""}

    try:
        if peticion.get("operacion") == "peticion" and "archivo" in peticion:
            archivo_solicitado = peticion["archivo"]
            respuesta["archivo"] = archivo_solicitado

            if existe_archivo(archivo_solicitado, archivos_existentes):
                respuesta["respuesta"] = "ACK"
            else:
                respuesta["respuesta"] = "NACK"
        else:
            respuesta["respuesta"] = "NACK"

    except Exception as e:
        print(f"Error creando respuesta: {e}")
        respuesta["respuesta"] = "NACK"

    return json.dumps(respuesta).encode("utf-8")


def manejar_peticion(sock: socket.socket, data: bytes, addr: tuple):
    try:
        peticion = peticion_recibida(data)
        print(f"Peticion recibida de {addr}: {peticion}")

        with archivos_lock:
            archivos_actuales = archivos_disponibles.copy()

        respuesta = crear_respuesta(peticion, archivos_actuales)
        sock.sendto(respuesta, addr)
        print(f"Respuesta enviada a {addr}")

    except Exception as e:
        print(f"Error manejando peticion de {addr}: {e}")

        error_response = json.dumps(
            {"operacion": "respuesta", "respuesta": "NACK", "archivo": ""}
        ).encode("utf-8")
        sock.sendto(error_response, addr)


def main():
    global archivos_disponibles

    if len(sys.argv) < 4:
        print(
            "Uso: python servidor.py <Carpeta/> <Archivos_ignorados.txt> <ttl_segundos>"
        )
        exit(-1)

    carpeta = sys.argv[1]
    archivo_indices = sys.argv[2]
    try:
        ttl_segundos = int(sys.argv[3])
    except ValueError:
        print("Error: TTL debe ser un numero entero")
        exit(-1)

    warm_file = "warm_file.txt"

    if exists(warm_file):
        print("Archivo warm encontrado, cargando...")
        archivos_iniciales = cargar_warm_file(warm_file)
        if not archivos_iniciales:
            nombres_a_saltar = leer_nombres_a_saltar(archivo_indices)
            archivos_iniciales = leer_archivos(carpeta, nombres_a_saltar, ttl_segundos)
    else:
        print("Archivo warm no encontrado, cargando desde 0")
        nombres_a_saltar = leer_nombres_a_saltar(archivo_indices)
        archivos_iniciales = leer_archivos(carpeta, nombres_a_saltar, ttl_segundos)
        guardar_warm_file(warm_file, archivos_iniciales)
        print(
            f"Archivo {warm_file} creado con {
                len(archivos_iniciales)} archivos iniciales"
        )

    if not archivos_iniciales:
        print("No se encontraron archivos en la carpeta seleccionada")
        exit(-1)

    with archivos_lock:
        archivos_disponibles = archivos_iniciales
    print(f"Archivos cargados inicialmente: {len(archivos_disponibles)}")

    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.bind((UDP_IP, UDP_PORT))
        print(f"Servidor UDP iniciado en {UDP_IP}:{UDP_PORT}")
    except socket.error as e:
        print(f"Error: {e} al crear socket, finalizando servidor...")
        exit(-1)

    hilo_actualizador = threading.Thread(
        target=actualizar_archivos,
        args=(carpeta, leer_nombres_a_saltar(archivo_indices), ttl_segundos, warm_file),
        daemon=True,
    )
    hilo_actualizador.start()
    print("Hilo de actualizacion de archivos iniciado")

    print("Servidor listo para recibir peticiones...")

    try:
        while True:
            data, addr = sock.recvfrom(1024)
            hilo_peticion = threading.Thread(
                target=manejar_peticion, args=(sock, data, addr), daemon=True
            )
            hilo_peticion.start()

    except Exception as e:
        print(f"Error en el servidor: {e}")
    finally:
        sock.close()
        print("Socket cerrado")


if __name__ == "__main__":
    main()
