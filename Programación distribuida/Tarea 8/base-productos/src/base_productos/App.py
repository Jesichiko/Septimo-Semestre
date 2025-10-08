from xmlrpc.server import SimpleXMLRPCServer
import xmlrpc.client
from services import CRUD
import time


def return_callback(callback_url, id: int) -> bool:
    try:
        proxy = xmlrpc.client.ServerProxy(callback_url)
        proxy.client_callback(id)
        print("Callback enviado con exito")
        return True
    except Exception as e:
        print(e)
        return False


def crear(callback_url, nombre: str, precio: int) -> bool:
    print(f'Creando producto "{nombre},{precio}"en el archivo xml')
    time.sleep(3)
    return return_callback(
        callback_url=callback_url, id=CRUD.create(nombre=nombre, precio=precio)
    )


def insertar(callback_url, id: int, nombre: str, precio: int) -> int:
    print(f'Insertando producto "id {id}:{nombre},{precio}"en el archivo xml')
    time.sleep(3)
    return return_callback(
        callback_url=callback_url,
        id=CRUD.insert(id=id, nombre=nombre, precio=precio),
    )


def consultar(callback_url, name: str) -> list() | int:
    print(f'Consultando producto con id:"{id}"en el archivo xml')
    time.sleep(3)
    return return_callback(callback_url=callback_url, id=CRUD.consult(name=name))


def init_server():
    server = SimpleXMLRPCServer(("::", 8080), allow_none=True)
    print("Servidor iniciando, escuchando en 8080")
    server.register_function(crear, "crear")
    server.register_function(insertar, "insertar")
    server.register_function(consultar, "consultar")
    server.serve_forever()


if __name__ == "__main__":
    init_server()
