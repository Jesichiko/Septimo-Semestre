import xmlrpc.client
from xmlrpc.server import SimpleXMLRPCServer
import threading
import time
import random
import string
import sys
from concurrent.futures import ThreadPoolExecutor

SERVER_URL = "http://localhost:8080"
callback_port = 9000
interval = float(sys.argv[1]) if len(sys.argv) > 1 else 3
proxy = xmlrpc.client.ServerProxy(SERVER_URL, allow_none=True)


def client_callback(producto_id):
    print(f"Callback recibido! Producto ID: {producto_id}")
    return True


def start_callback_server():
    server = SimpleXMLRPCServer(
        ("localhost", callback_port), allow_none=True, logRequests=False
    )
    server.register_function(client_callback, "client_callback")
    print(f"Servidor de callback iniciado en localhost:{callback_port}")
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
        resultado = proxy.crear(f"http://localhost:{callback_port}", nombre, precio)
        print(f"[CREAR] {nombre}, {precio} -> {resultado}")

    executor.submit(task)


def async_insertar(producto_id, nombre, precio):
    def task():
        try:
            resultado = proxy.insertar(
                f"http://localhost:{callback_port}", producto_id, nombre, precio
            )
            print(f"[INSERTAR] ID {producto_id}: {nombre}, {precio} -> {resultado}")
        except Exception as e:
            print(f"[ERROR async_insertar]: {e}")

    executor.submit(task)


def async_consultar(nombre):
    def task():
        resultado = proxy.consultar(f"http://localhost:{callback_port}", nombre)
        print(f"[CONSULTAR] {nombre} -> {resultado}")

    executor.submit(task)


# -------------------------------
# Loop principal
# -------------------------------
next_id = 1
while True:
    try:
        nombre_crear = random_name()
        precio_crear = random_price()
        print(f"PETICION: CREAR enviada -> ({nombre_crear},{precio_crear})")
        async_crear(nombre_crear, precio_crear)

        nombre_insert = random_name()
        precio_insert = random_price()
        print(
            f"PETICION: INSERTAR enviada -> (#{next_id},{nombre_insert},{
                precio_insert
            })"
        )
        async_insertar(next_id, nombre_insert, precio_insert)

        next_id += 1
        nombre_consulta = random.choice([nombre_crear, nombre_insert, random_name()])
        print(f"PETICION: CONSULTA enviada -> ({nombre_consulta})")
        async_consultar(nombre_consulta)

        print(f"Esperando {interval} segundos para nuevas peticiones...")
        time.sleep(interval)
    except KeyboardInterrupt:
        print("\nCliente detenido manualmente")
        break
