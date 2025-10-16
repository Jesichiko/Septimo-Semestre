from grpc import StatusCode

from grpc_tarea.protos import operation_service_pb2, operation_service_pb2_grpc
from grpc_tarea.utils.interfaces.execute import ExecuteOperation
from grpc_tarea.utils.interfaces.parser import Parser


class OperacionServicer(operation_service_pb2_grpc.AritmeticaServiceServicer):
    def __init__(self, operation_parser: Parser, operation_executor: ExecuteOperation):
        self.parser = operation_parser
        self.exec_operation = operation_executor

    def Operacion(self, request, context):
        # Validamos request completo
        validation_result = self._validate_request(request, context)
        if not validation_result["valid"]:
            return operation_service_pb2.OperacionResponse()

        # Construimos lista de operaciones
        requested_operation = self._build_operation_list(
            validation_result["data"], request
        )
        print(f"[SERVICIO PEDIDO] Operacion recibida: {requested_operation}\n")

        # Parseamos operaciones con el Parser dado
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

        # Ejecutamos operaciones con el Executor dado
        result = self.exec_operation(parsed_operations)
        if result is None:
            print(
                "[ERROR SERVICIO EXECUTER] Operacion invalida (division por 0 u otro error)"
            )
            context.set_code(StatusCode.ABORTED)
            context.set_details("Operacion invalida (division por 0)")
            return operation_service_pb2.OperacionResponse()

        print(f"[SERVICIO EXITOSO] Resultado exitoso: {result}\n")
        return operation_service_pb2.OperacionResponse(result=result)

    def _validate_request(self, request, context):
        result = {"valid": False, "data": {}}

        # 1. Validamos que num1 exista
        if not request.num1 or request.num1.strip() == "":
            print("[ERROR SERVICIO VALIDACION] num1 no proporcionado o vacio")
            context.set_code(StatusCode.INVALID_ARGUMENT)
            context.set_details("Campo requerido: num1 debe estar presente y no vacio")
            return result

        # 2. Validamos formato de num1 (string valido convertible a float)
        try:
            num1_value = float(request.num1)
        except ValueError:
            print(
                f"[ERROR SERVICIO VALIDACION] num1 '{
                    request.num1
                }' tiene formato invalido"
            )
            context.set_code(StatusCode.INVALID_ARGUMENT)
            context.set_details(
                f"Formato invalido: num1 debe ser un numero valido, recibido '{
                    request.num1
                }'"
            )
            return result

        # 3. Validamos que operador necesario exista
        if not request.operacion or request.operacion.strip() == "":
            print("[ERROR SERVICIO VALIDACION] operador no proporcionado o vacio")
            context.set_code(StatusCode.INVALID_ARGUMENT)
            context.set_details(
                "Campo requerido: operacion debe estar presente y no vacia"
            )
            return result

        # 4. Validamos que exista num2 O operaciones adicionales
        has_num2 = request.num2 and request.num2.strip() != ""
        has_opts = len(request.opts_operaciones) > 0

        if not has_num2:
            print(
                f"[ERROR SERVICIO VALIDACION] Operacion incompleta: falta segundo operando para '{
                    request.operacion
                }'"
            )
            context.set_code(StatusCode.INVALID_ARGUMENT)
            context.set_details(
                f"Operacion incompleta: se requiere num2 para '{
                    request.operacion
                }'"
            )
            return result

        # 5. Validamos formato de num2 si existe
        num2_value = None
        if has_num2:
            try:
                num2_value = float(request.num2)
            except ValueError:
                print(
                    f"[ERROR SERVICIO VALIDACION] num2 '{
                        request.num2
                    }' tiene formato invalido"
                )
                context.set_code(StatusCode.INVALID_ARGUMENT)
                context.set_details(
                    f"Formato invalido: num2 debe ser un numero valido, recibido '{
                        request.num2
                    }'"
                )
                return result

        # 6. Validamos operaciones adicionales si existen
        if has_opts:
            opts_validation = self._validate_optional_operations(
                request.opts_operaciones, context
            )
            if not opts_validation["valid"]:
                return result
            result["data"]["opts"] = opts_validation["data"]

        # Todo valido
        result["valid"] = True
        result["data"]["num1"] = num1_value
        result["data"]["operacion"] = request.operacion
        result["data"]["num2"] = num2_value
        return result

    def _validate_optional_operations(self, opts_operaciones, context):
        result = {"valid": False, "data": []}
        validated_ops = []

        for idx, op in enumerate(opts_operaciones):
            # Validamos que operador exista
            if not op.operacion or op.operacion.strip() == "":
                print(
                    f"[ERROR SERVICIO VALIDACION] Operacion adicional {
                        idx
                    }: operador no proporcionado o vacio"
                )
                context.set_code(StatusCode.INVALID_ARGUMENT)
                context.set_details(
                    f"Operacion adicional {
                        idx
                    }: operador requerido y no puede estar vacio"
                )
                return result

            # Validamos que numero exista
            if not op.numero or op.numero.strip() == "":
                print(
                    f"[ERROR SERVICIO VALIDACION] Operacion adicional {
                        idx
                    }: numero no proporcionado o vacio"
                )
                context.set_code(StatusCode.INVALID_ARGUMENT)
                context.set_details(
                    f"Operacion adicional {
                        idx
                    }: numero requerido y no puede estar vacio"
                )
                return result

            # Validamos formato del numero (string valido convertible a float)
            try:
                num_value = float(op.numero)
            except ValueError:
                print(
                    f"[ERROR SERVICIO VALIDACION] Operacion adicional {idx}: numero '{
                        op.numero
                    }' tiene formato invalido"
                )
                context.set_code(StatusCode.INVALID_ARGUMENT)
                context.set_details(
                    f"Operacion adicional {idx}: numero debe ser valido, recibido '{
                        op.numero
                    }'"
                )
                return result

            validated_ops.append((op.operacion, num_value))

        result["valid"] = True
        result["data"] = validated_ops
        return result

    def _build_operation_list(self, validated_data, request):
        operation_list = [
            validated_data["num1"],
            validated_data["operacion"],
        ]

        # Agregamos num2 si existe
        if validated_data["num2"] is not None:
            operation_list.append(validated_data["num2"])

        # Agregamos operaciones adicionales si existen
        if "opts" in validated_data:
            for operador, numero in validated_data["opts"]:
                operation_list.append(operador)
                operation_list.append(numero)

        return operation_list
