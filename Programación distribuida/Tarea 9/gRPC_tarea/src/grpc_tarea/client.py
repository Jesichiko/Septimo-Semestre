import grpc
from grpc_tarea.protos import operation_service_pb2, operation_service_pb2_grpc


def run_client():
    with grpc.insecure_channel("localhost:8080") as channel:
        stub = operation_service_pb2_grpc.AritmeticaServiceStub(channel=channel)
        num1 = 15
        operacion = "+"
        request = operation_service_pb2.OperacionRequest(
            num1=num1, operacion=operacion, 
        )

        try:
            response = stub.Operacion(request=request)
            print(f"Respuesta de la operacion: {response}")
        except grpc.RpcError as e:
            print(f"Error al al llamar al servidor: {e.code()} - {e.details()}")
