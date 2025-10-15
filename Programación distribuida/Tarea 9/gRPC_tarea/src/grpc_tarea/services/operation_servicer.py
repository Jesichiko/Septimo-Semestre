from grpc_tarea.protos import operation_service_pb2, operation_service_pb2_grpc
from grpc import StatusCode


class OperacionServicer(operation_service_pb2_grpc.AritmeticaServiceServicer):
    def __init__(self, operation_parser, operation_executor):
        self.parser = operation_parser
        self.exec_operation = operation_executor

    def Operacion(self, request, context):
        requested_operation = [request.num1, request.operacion, request.num2]
        for op in request.opts_operaciones:
            requested_operation.append(op.operacion)
            requested_operation.append(op.numero)

        parsed_operations = self.parser.parse_operation(requested_operation)
        if not parsed_operations:
            print(f"Error: Peticion {request} no legible")
            context.set_code(StatusCode.INVALID_ARGUMENT)
            context.set_details("Peticion con formato erroneo")
            return operation_service_pb2.OperacionResponse()

        return operation_service_pb2.OperacionResponse(
            result=self.exec_operation(parsed_operations)
        )
