from grpc import StatusCode
from grpc_services.protos import numbers_service_pb2, numbers_service_pb2_grpc
from grpc_services.utils.generate_random_numbers import Generate_Numbers


class NumbersServicer(numbers_service_pb2_grpc.NumbersServiceServicer):
    def __init__(self, number_generator: Generate_Numbers):
        self.generator = number_generator
        pass

    def getNumbers(self, request, context):
        print("[SERVER: SERVICIO NUMBERS] Peticion recibida de pedido de numeros")
        try:
            numbers = self.generator.getNumbers()
            print("[SERVICIO NUMBERS: EXITO] Vector de numeros creados con exito")
        except Exception as e:
            print("[SERVICIO NUMBERS: ERROR] Error al crear vector de numeros")
            context.set_code(StatusCode.ABORTED)
            context.set_details(f"Error al crear vector de numeros: {e}")

        return numbers_service_pb2.NumbersResponse(
            num1=numbers[0], num2=numbers[1], num3=numbers[2]
        )
