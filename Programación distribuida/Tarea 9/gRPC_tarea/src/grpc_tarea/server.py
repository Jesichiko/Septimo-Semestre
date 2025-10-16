import sys
from concurrent import futures

import grpc

from grpc_tarea.protos import operation_service_pb2_grpc
from grpc_tarea.services.operation_servicer import OperacionServicer
from grpc_tarea.utils.implementations.list_operation_parser import ListOperationParser
from grpc_tarea.utils.implementations.operation_executer import PostfixOperationExecuter
from grpc_tarea.utils.interfaces.execute import ExecuteOperation
from grpc_tarea.utils.interfaces.parser import Parser


def serve(
    host="0.0.0.0",
    port=8080,
    max_workers=10,
    parser_ops: Parser = None,
    executor_op: ExecuteOperation = None,
):
    # parser y executor a utilizar
    parser = parser_ops or ListOperationParser()
    executor = executor_op or PostfixOperationExecuter.exec_operation

    # iniciamos la config del servidor:
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=max_workers))
    operation_service_pb2_grpc.add_AritmeticaServiceServicer_to_server(
        OperacionServicer(parser, executor), server
    )
    server_address = f"{host}:{port}"
    server.add_insecure_port(server_address)

    # iniciamos el servidor:
    server.start()

    print("Servidor gRPC de operaciones iniciado")
    print("=" * 60)
    print(f"Direccion IP: {server_address}")
    print(f"Workers: {max_workers}")
    print("=" * 60)
    print("\nEsperando peticiones...\n")

    try:
        server.wait_for_termination()
    except KeyboardInterrupt:
        print("\n\nServidor detenido manualmente")
        server.stop(0)


def main():
    try:
        host = sys.argv[1] if len(sys.argv) > 1 else "0.0.0.0"
        port = int(sys.argv[2]) if len(sys.argv) > 2 else 8080
        max_workers = int(sys.argv[3]) if len(sys.argv) > 3 else 10
    except (ValueError, IndexError):
        host, port, max_workers = "0.0.0.0", 50051, 10

    serve(host, port, max_workers)


if __name__ == "__main__":
    main()
