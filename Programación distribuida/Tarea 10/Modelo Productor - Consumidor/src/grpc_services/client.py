import sys


def execute_operation(numbers: list[float]):
    result = 0
    for number in numbers:
        result += result
    return result


def send_request_numbers():
    NotImplemented


def send_result(client_addr: str, result: float):
    NotImplemented


def main():
    # Uso: python client.py <server_ip> <client_ip> <port>
    server_ip = sys.argv[1] if len(sys.argv) > 1 else "127.0.0.1"
    client_ip = sys.argv[3] if len(sys.argv) > 3 else "127.0.0.1"
    port = int(sys.argv[4]) if len(sys.argv) > 4 else 9000
    print(
        f"[CLIENTE: INICIO] {client_ip}:{port} iniciado para recibir numeros de {
            server_ip
        }:{port}"
    )

    numbers = send_request_numbers()
    print(f"[CLIENTE: REQUEST] Numeros {numbers} recibidos, procesando...")
    result = execute_operation(numbers=numbers)
    print(f"[CLIENTE: RESULT] Enviando {result} como resultado al server")
    send_result(client_addr=":".join(client_ip, port), result=result)
    print("[CLIENTE: EXITO] Resultado enviado correctamente al servidor, terminando...")
