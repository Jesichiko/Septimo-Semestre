from grpc import StatusCode
from grpc_services.protos import numbers_service_pb2, numbers_service_pb2_grpc
from grpc_services.utils.generate_random_numbers import Generate_Numbers
from grpc_services.utils.user_stats import UserStats


class NumbersServicer(numbers_service_pb2_grpc.NumbersServiceServicer):
    def __init__(self, number_generator: Generate_Numbers, user_stats: UserStats):
        self.generator = number_generator
        self.stats = user_stats
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
            return numbers_service_pb2.NumbersResponse()

        return numbers_service_pb2.NumbersResponse(
            num1=numbers[0], num2=numbers[1], num3=numbers[2]
        )

    def receiveResult(self, request, context):
        if not request.user_addr or request.user_addr.strip() == "":
            print("[ERROR RECEIVE RESULT] Direccion de usuario invalida")
            context.set_code(StatusCode.INVALID_ARGUMENT)
            context.set_details("Campo IP invalido en mensaje")
            return numbers_service_pb2.ResultResponse(response=False)

        if not request.result:
            print("[ERROR RECEIVE RESULT] Resultado no proporcionado")
            context.set_code(StatusCode.INVALID_ARGUMENT)
            context.set_details("Resultado no proporcionado en mensaje")
            return numbers_service_pb2.ResultResponse(response=False)

        print(
            f"[SERVER: RECEIVE RESULT] Resultado {request.result} recibido de {
                request.user_addr
            }"
        )

        self.stats.addResult(request.user_addr, request.result)
        print("[SERVER: RESULTADO REGISTRADO] Resultado almacenado exitosamente")
        return numbers_service_pb2.ResultResponse(response=True)
