from grpc import StatusCode

from grpc_tarea.protos import operation_service_pb2, operation_service_pb2_grpc
from grpc_tarea.utils.interfaces.execute import ExecuteOperation
from grpc_tarea.utils.interfaces.parser import Parser


class OperacionServicer(operation_service_pb2_grpc.AritmeticaServiceServicer):
    def __init__(self, operation_parser: Parser, operation_executor: ExecuteOperation):
        self.parser = operation_parser
        self.exec_operation = operation_executor

    def Operacion(self, request, context):
        # Construir la lista de operaciones solo si tenemos datos válidos
        requested_operation = []

        # Validamos que tengamos al menos num1 y operacion
        if request.num1 == 0.0 and request.num2 == 0.0 and not request.opts_operaciones:
            print("[ERROR SERVICIO] Peticion vacia o invalida")
            context.set_code(StatusCode.INVALID_ARGUMENT)
            context.set_details(
                "La peticion debe contener al menos una operación válida"
            )
            return operation_service_pb2.OperacionResponse()
        requested_operation.append(request.num1)

        # Si tenemos operacion, debe haber num2 O opts_operaciones
        if request.operacion:
            requested_operation.append(request.operacion)

            # Si hay num2 definido:
            if request.num2 != 0.0 or request.opts_operaciones:
                requested_operation.append(request.num2)
            else:
                # Operacion incompleta: tenemos operador pero no segundo operando
                print(
                    f"[ERROR SERVICIO] Operacion incompleta: falta el segundo operando para '{
                        request.operacion
                    }'"
                )
                context.set_code(StatusCode.INVALID_ARGUMENT)
                context.set_details(
                    "Operacion incompleta: falta el segundo operando minimo"
                )
                return operation_service_pb2.OperacionResponse()

        # Agregamos operaciones adicionales
        for op in request.opts_operaciones:
            if not op.operacion:
                print("[ERROR SERVICIO] Operacion adicional sin operador")
                context.set_code(StatusCode.INVALID_ARGUMENT)
                context.set_details("Operacion adicional invalida: falta operador")
                return operation_service_pb2.OperacionResponse()
            requested_operation.append(op.operacion)
            requested_operation.append(op.numero)

        print(f"[SERVICIO PEDIDO] Operacion recibida: {requested_operation}")

        # Parseamos las operaciones:
        parsed_operations = self.parser.parse_operation(requested_operation)
        if parsed_operations is None:
            print(
                f"[ERROR SERVICIO PARSER] Peticion {
                    requested_operation
                } no legible (formato erroneo)"
            )
            context.set_code(StatusCode.INVALID_ARGUMENT)
            context.set_details("Peticion con formato erroneo - no se pudo parsear")
            return operation_service_pb2.OperacionResponse()

        # Ejecutamos las operaciones:
        result = self.exec_operation(parsed_operations)
        if result is None:
            print("[ERROR SERVICIO EXECUTER] Operacion invalida (division por 0)")
            context.set_code(StatusCode.ABORTED)
            context.set_details("Operacion invalida (division por 0)")
            return operation_service_pb2.OperacionResponse()

        print(f"[SERVICIO EXITOSO] Resultado exitoso: {result}\n")
        return operation_service_pb2.OperacionResponse(result=result)
