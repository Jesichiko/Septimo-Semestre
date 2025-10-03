import threading
from xmlrpc.server import SimpleXMLRPCRequestHandler, SimpleXMLRPCServer
from .services import user_priority
import xmlrpc.client

x: int = 0
queue = user_priority.FairQueue()
_thread_local = threading.local()


class MyHandler(SimpleXMLRPCRequestHandler):
    def handle(self):
        _thread_local.client_ip = self.client_address[0]
        try:
            super().handle()
        finally:
            _thread_local.client_ip = None


def get_client_ip():
    return getattr(_thread_local, "client_ip", None)


def counter() -> int:
    global x

    x += 1
    print(f"Valor de la variable actualizado a {x}")
    if x >= 1000:
        users = queue.users()
        for ip in users:
            try:
                proxy = xmlrpc.client.ServerProxy(f"http://{ip}:9090/")
                proxy.cliente.apagar()
                print(f"Apagando cliente {ip}")
            except Exception as e:
                print(f"No se pudo apagar {ip}: {e}")
    return x


def process_request() -> bool:
    ip = get_client_ip()
    if not ip:
        return False

    # solo IP
    queue.add(ip, None)

    # si la IP del usuario es la de su turno le toca
    if queue.is_turn(ip):
        queue.next_turn()
        return True
    else:  # si no retornamos false
        return False


def contador() -> int | str:
    if process_request():
        return counter()
    return "No es tu turno"


def main():
    with SimpleXMLRPCServer(
        ("0.0.0.0", 8080), requestHandler=MyHandler, allow_none=True
    ) as server:
        server.register_function(contador, "contador")
        server.serve_forever()


if __name__ == "__main__":
    main()
