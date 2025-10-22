import sys
import grpc
from concurrent import futures
import signal
import time

from grpc_services.protos import numbers_service_pb2_grpc
from grpc_services.services.numbers_servicer import NumbersServicer
from grpc_services.utils.generate_random_numbers import Generate_Numbers
from grpc_services.utils.user_stats import UserStats


def serve(host: str, port: str, workers: int):
    # utilidades a usar
    number_generator = Generate_Numbers()  # generador de nums
    user_stats = UserStats()  # estadisticas de trabajo de usuarios

    # añadimos el servicio a publicar, que es NumbersServicer
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=workers))
    numbers_service_pb2_grpc.add_NumbersServiceServicer_to_server(
        NumbersServicer(number_generator=number_generator, user_stats=user_stats), server
    )

    # iniciamos server
    server_address = f"{host}:{port}"
    server.add_insecure_port(server_address)
    server.start()

    print(f"[SERVER: INICIO] Servidor escuchando en {server_address}...")
    print("[SERVER: LISTO] Esperando peticiones de clientes...")
    print("Presiona Ctrl+C para ver estadísticas y detener el servidor\n")

    print("Servidor gRPC de producto-consumidor iniciado")
    print("=" * 60)
    print(f"Direccion IP: {server_address}")
    print(f"Workers: {workers}")
    print("=" * 60)
    print("\nEsperando peticiones...\n")

    try:
        server.wait_for_termination()
    except KeyboardInterrupt:
        print("\n\nServidor detenido manualmente")
        server.stop(0)


def main():
    # Argumentos: python <ip_server> <port_server> <workers>
    try:
        host = sys.argv[1] if len(sys.argv) > 1 else "0.0.0.0"
        port = int(sys.argv[2]) if len(sys.argv) > 2 else 8080
        max_workers = int(sys.argv[3]) if len(sys.argv) > 3 else 10
    except (ValueError, IndexError):
        host, port, max_workers = "0.0.0.0", 50051, 10

    serve(host, port, max_workers)


if __name__ == "__main__":
    main()
