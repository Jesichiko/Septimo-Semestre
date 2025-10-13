import xmlrpc.client
from xmlrpc.server import SimpleXMLRPCServer
import threading
import time
import random
import string
import sys
from concurrent.futures import ThreadPoolExecutor

# Uso: python client.py <server_ip> <server_port> <client_ip> <callback_port> <interval> <next_id>
server_ip = sys.argv[1] if len(sys.argv) > 1 else "127.0.0.1"
server_port = int(sys.argv[2]) if len(sys.argv) > 2 else 8080
client_ip = sys.argv[3] if len(sys.argv) > 3 else "127.0.0.1"
callback_port = int(sys.argv[4]) if len(sys.argv) > 4 else 9000
interval = float(sys.argv[5]) if len(sys.argv) > 5 else 3
next_id = int(sys.argv[6]) if len(sys.argv) > 6 else 10

SERVER_URL = f"http://{server_ip}:{server_port}"
CALLBACK_URL = f"http://{client_ip}:{callback_port}"


def client_callback(producto_id):
    if producto_id > 0:
        print(f"[CALLBACK EXITOSO] Producto ID: {producto_id}")
    elif producto_id == -1:
        print(f"[CALLBACK ERROR] La operación fallo (ID: {producto_id})")
    return True


def start_callback_server():
    server = SimpleXMLRPCServer(
        (client_ip, callback_port), allow_none=True, logRequests=False
    )
    server.register_function(client_callback, "client_callback")
    print(f"Servidor de callback iniciado en {client_ip}:{callback_port}")
    print(f"Conectando al servidor en {SERVER_URL}\n")
    server.serve_forever()


threading.Thread(target=start_callback_server, daemon=True).start()
time.sleep(1)


def random_name(length=6):
    return "".join(random.choices(string.ascii_letters, k=length))


def random_price(min_val=10, max_val=1000):
    return random.randint(min_val, max_val)


executor = ThreadPoolExecutor(max_workers=5)


def async_crear(nombre, precio):
    def task():
        try:
            proxy = xmlrpc.client.ServerProxy(SERVER_URL, allow_none=True)
            resultado = proxy.crear(CALLBACK_URL, nombre, precio)
            print(f"[CREAR] {nombre}, {precio} -> {resultado}")
        except Exception as e:
            print(f"[ERROR async_crear]: {e}")

    executor.submit(task)


def async_insertar(producto_id, nombre, precio):
    def task():
        try:
            proxy = xmlrpc.client.ServerProxy(SERVER_URL, allow_none=True)
            resultado = proxy.insertar(CALLBACK_URL, producto_id, nombre, precio)
            print(f"[INSERTAR] ID {producto_id}: {nombre}, {precio} -> {resultado}")
        except Exception as e:
            print(f"[ERROR async_insertar]: {e}")

    executor.submit(task)


def async_consultar(nombre):
    def task():
        try:
            proxy = xmlrpc.client.ServerProxy(SERVER_URL, allow_none=True)
            resultado = proxy.consultar(CALLBACK_URL, nombre)
            print(f"[CONSULTAR] {nombre} -> {resultado}")
        except Exception as e:
            print(f"[ERROR async_consultar]: {e}")

    executor.submit(task)


# Loop principal
print("CONFIGURACION DEL CLIENTE")
print("=" * 60)
print(f"Servidor remoto: {SERVER_URL}")
print(f"Cliente local: {CALLBACK_URL}")
print(f"Intervalo: {interval} segundos")
print(f"ID inicial: {next_id}")
print("=" * 60)
print()

while True:
    try:
        nombre_crear = random_name()
        precio_crear = random_price()
        print(f"PETICION: CREAR enviada -> ({nombre_crear},{precio_crear})")
        async_crear(nombre_crear, precio_crear)

        nombre_insert = random_name()
        precio_insert = random_price()
        print(
            f"PETICION: INSERTAR enviada -> (#{next_id},{nombre_insert},{precio_insert})"
        )
        async_insertar(next_id, nombre_insert, precio_insert)

        next_id += 1
        nombre_consulta = random.choice([nombre_crear, nombre_insert, random_name()])
        print(f"PETICION: CONSULTA enviada -> ({nombre_consulta})")
        async_consultar(nombre_consulta)

        print(f"Esperando {interval} segundos para nuevas peticiones...\n")
        time.sleep(interval)
    except KeyboardInterrupt:
        print("\nCliente detenido manualmente")
        executor.shutdown(wait=True)
        break
