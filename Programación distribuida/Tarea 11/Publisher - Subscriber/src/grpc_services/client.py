import sys
import grpc
import random
from google.protobuf import empty_pb2

from grpc_services.protos import numbers_service_pb2, numbers_service_pb2_grpc


def execute_operation(numbers: list[float]) -> float:
    result = 0.0
    for number in numbers:
        result += number
    return result


def send_request_numbers(server_address: str) -> tuple(list[int], list[str]):
    try:
        with grpc.insecure_channel(server_address) as channel:
            stub = numbers_service_pb2_grpc.NumbersServiceStub(channel)
            response = stub.getNumbers(
                numbers_service_pb2.NumbersRequest(
                    num_queues=1 if random.random() <= 0.50 else 2
                )
            )
            return (
                [response.num1, response.num2, response.num3],
                list(response.publishers),
            )
    except grpc.RpcError as e:
        print(
            f"[REQUESTED NUMBERS: ERROR] Error al solicitar numeros: {e.code()}: {
                e.details()
            }"
        )
        raise
    except Exception as e:
        print(f"[REQUESTED NUMBERS: ERROR] {e}")
        raise


def send_result(
    server_address: str, client_addr: str, result: float, publishers: list[str]
) -> bool:
    try:
        with grpc.insecure_channel(server_address) as channel:
            stub = numbers_service_pb2_grpc.NumbersServiceStub(channel)
            request = numbers_service_pb2.ResultRequest(
                user_addr=client_addr, result=result, subscribed=publishers
            )
            response = stub.receiveResult(request)
            return response.response
    except grpc.RpcError as e:
        print(
            f"[SEND RESULT: ERROR] Error al enviar resultado: {e.code()}: {e.details()}"
        )
        return False
    except Exception as e:
        print(f"[SEND RESULT: ERROR] Error inesperado: {e}")
        return False


def main():
    # Argumentos: python client.py <server_ip> <server_port> <client_ip> <client_port>
    server_ip = sys.argv[1] if len(sys.argv) > 1 else "0.0.0.0"
    client_ip = sys.argv[2] if len(sys.argv) > 3 else "0.0.0.0"
    port = int(sys.argv[3]) if len(sys.argv) > 4 else 8080

    server_address = f"{server_ip}:{port}"
    client_addr = f"{client_ip}:{port}"
    print(f"[CLIENTE: INICIO] {client_addr} conectando a servidor {server_address}")
    try:
        numbers, publishers = send_request_numbers(server_address=server_address)
        print(f"[CLIENTE: REQUEST] Numeros recibidos: {numbers}, procesando...")

        result = execute_operation(numbers=numbers)
        print(f"[CLIENTE: RESULT] Resultado calculado: {result}")

        print("[CLIENTE: ENVIANDO RESULT] Enviando resultado al servidor...")
        success = send_result(
            server_address=server_address,
            client_addr=client_addr,
            result=result,
            publishers=publishers,
        )

        if success:
            print("[CLIENTE: EXITO] Resultado enviado correctamente, terminando...")
        else:
            print("[CLIENTE: ERROR] No se pudo enviar el resultado correctamente")
            sys.exit(1)

    except Exception as e:
        print(f"[CLIENTE: ERROR] {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
