from grpc import StatusCode
from grpc_services.protos import numbers_service_pb2, numbers_service_pb2_grpc
from grpc_services.utils.generate_random_numbers import Generate_Numbers
from grpc_services.utils.user_stats import UserStats


class NumbersServicer(numbers_service_pb2_grpc.NumbersServiceServicer):
    def __init__(self, number_generator: Generate_Numbers, user_stats: UserStats):
        self.generator = number_generator
        self.stats = user_stats

    def getNumbers(self, request, context):
        print("[SERVER: REQUESTED NUMBERS] Peticion recibida de pedido de numeros...")
        if not request.num_queues:
            print(
                "[REQUESTED NUMBERS: ERROR] No se recibio numero de queues para tomar numeros\n"
            )
            context.set_code(StatusCode.INVALID_ARGUMENT)
            context.set_details("No se recibio numero de queues para tomar numeros")
            return numbers_service_pb2.NumbersResponse()

        try:
            numbers, publishers = self.generator.getNumbers()
            print("[REQUESTED NUMBERS: EXITO] Vector de numeros creados con exito:")
            print(f"Numeros: {numbers}")
            print(f"Publishers:{publishers}\n")
        except Exception as e:
            print("[REQUESTED NUMBERS: ERROR] Error al crear vector de numeros\n")
            context.set_code(StatusCode.ABORTED)
            context.set_details(f"Error al crear vector de numeros: {e}")
            return numbers_service_pb2.NumbersResponse()

        return numbers_service_pb2.NumbersResponse(
            num1=numbers[0], num2=numbers[1], num3=numbers[2], publishers=publishers
        )

    def receiveResult(self, request, context):
        print("[SERVER: RECEIVED RESULT] Verificando mensaje recibido...")

        if not request.user_addr or request.user_addr.strip() == "":
            print("[RESULT RECEIVED: ERROR] Direccion de usuario invalida\n")
            context.set_code(StatusCode.INVALID_ARGUMENT)
            context.set_details("Campo IP invalido en mensaje")
            return numbers_service_pb2.ResultResponse(response=False)

        if not request.result:
            print("[RESULT RECEIVED: ERROR] Resultado no proporcionado\n")
            context.set_code(StatusCode.INVALID_ARGUMENT)
            context.set_details("Resultado no proporcionado en mensaje")
            return numbers_service_pb2.ResultResponse(response=False)

        if not len(request.subscribed) > 0:
            print("[RESULT RECEIVED: ERROR] Publishers suscritos no proporcionados\n")
            context.set_code(StatusCode.INVALID_ARGUMENT)
            context.set_details("Publishers suscritos no proporcionados")
            return numbers_service_pb2.ResultResponse(response=False)

        self.stats.addResult(request.user_addr, request.result, request.subscribed)
        print("[SERVER: RESULTADO REGISTRADO] Resultado almacenado exitosamente\n")

        # mostramos stats actuales de todos los usuarios que dieron resultado
        print("[ESTADISTICAS USUARIOS]")
        print("-" * 60)
        self.stats.print_statistics()
        print("\n")

        return numbers_service_pb2.ResultResponse(response=True)
