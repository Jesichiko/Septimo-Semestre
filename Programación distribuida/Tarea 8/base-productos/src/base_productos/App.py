import sys
import time
import xmlrpc.client
from xmlrpc.server import SimpleXMLRPCServer
from queue import PriorityQueue
import threading
from .db import Database

# Cola de prioridades: 0 = alta (crear/insertar), 1 = baja (consultar)
task_queue = PriorityQueue()


def return_callback(callback_url: str, producto_id: int) -> bool:
    try:
        proxy = xmlrpc.client.ServerProxy(callback_url, allow_none=True)
        proxy.client_callback(producto_id)
        print(f"[CALLBACK] enviado con exito: producto_id = {producto_id}")
        return True
    except Exception as e:
        print(f"[ERROR CALLBACK]: No se envio callback: {e}")
        return False


def process_tasks(db: Database):
    # Worker que procesa tareas de la cola segun prioridad
    while True:
        priority, task_data = task_queue.get()
        task_type, callback_url, args = task_data

        try:
            if task_type == "CREAR":
                nombre, precio = args
                time.sleep(3)
                producto_id = db.create_item(name=nombre, precio=precio)
                return_callback(callback_url, producto_id)

            elif task_type == "INSERTAR":
                id_product, nombre, precio = args
                time.sleep(3)
                producto_id = db.insert_item(
                    id_product=id_product, name=nombre, precio=precio
                )
                return_callback(callback_url, producto_id)

            elif task_type == "CONSULTAR":
                nombre = args[0]
                time.sleep(3)
                producto_id = db.search_item(nombre)
                return_callback(callback_url, producto_id)

        except Exception as e:
            print(f"Error procesando tarea {task_type}: {e}")
            return_callback(callback_url, -1)

        task_queue.task_done()


def crear(db: Database, callback_url: str, nombre: str, precio: int) -> bool:
    # Prioridad 0 = alta (creaciones/inserciones primero)
    task_queue.put((0, ("CREAR", callback_url, (nombre, precio))))
    print(
        f"[PETICION] CREAR recibida y encolada \n\t -> Nombre:{nombre}, Precio:{
            precio
        } MXN"
    )
    return True


def insertar(
    db: Database, callback_url: str, id_product: int, nombre: str, precio: int
) -> bool:
    # Prioridad 0 = alta (creaciones/inserciones primero)
    task_queue.put((0, ("INSERTAR", callback_url, (id_product, nombre, precio))))
    print(
        f"[PETICION] INSERTAR recibida y encolada \n\t-> Id:#{id_product}, Nombre:{
            nombre
        }, Precio:{precio} MXN"
    )
    return True


def consultar(db: Database, callback_url: str, name: str) -> bool:
    # Prioridad 1 = baja (consultas despues de inserciones)
    task_queue.put((1, ("CONSULTAR", callback_url, (name,))))
    print(f"[PETICION] CONSULTAR recibida y encolada \n\t -> Nombre:{name}")
    return True


def init_server(db: Database, ip: str, port: int):
    # Iniciamos workers para procesar la cola
    for _ in range(10):
        worker = threading.Thread(target=process_tasks, args=(db,), daemon=True)
        worker.start()

    server = SimpleXMLRPCServer((ip, port), allow_none=True, logRequests=False)
    print(f"Servidor iniciado en {ip}:{port}\n\n\n")

    server.register_function(lambda *args: crear(db, *args), "crear")
    server.register_function(lambda *args: insertar(db, *args), "insertar")
    server.register_function(lambda *args: consultar(db, *args), "consultar")

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nServidor detenido manualmente.")
        print(f"Tareas pendientes en cola: {task_queue.qsize()}")


def main():
    try:
        ip = sys.argv[1] if len(sys.argv) > 1 else "0.0.0.0"
        port = int(sys.argv[2]) if len(sys.argv) > 2 else 8080
        parser_name = sys.argv[3] if len(sys.argv) > 3 else "xml"
        db_path = sys.argv[4] if len(sys.argv) > 4 else "db/products.xml"
    except (IndexError, ValueError):
        ip, port, parser_name, db_path = "0.0.0.0", 8080, "xml", "db/products.xml"

    if parser_name.lower() == "xml":
        if "/" in db_path:
            dir_name = "/".join(db_path.split("/")[:-1])
            file_name = db_path.split("/")[-1]
        else:
            dir_name, file_name = ".", db_path

        db_instance = Database(name=file_name, dir=dir_name)
    else:
        raise ValueError(f"Parser '{parser_name}' no soportado")

    print(f"Usando parser: {parser_name.upper()}")
    print(f"Base de datos: {db_path}")
    init_server(db_instance, ip, port)


if __name__ == "__main__":
    main()
