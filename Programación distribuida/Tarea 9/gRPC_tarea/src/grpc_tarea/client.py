import grpc

from grpc_tarea.protos import operation_service_pb2, operation_service_pb2_grpc


def test_operation(
    stub, description, num1, operacion, num2=None, opts_operaciones=None
):
    """Helper para probar operaciones - ahora convierte números a strings"""
    print(f"\n{'=' * 60}")
    print(f"TEST: {description}")
    print(f"{'=' * 60}")

    # Construimos request
    kwargs = {"num1": str(num1), "operacion": operacion}

    if num2 is not None:
        kwargs["num2"] = str(num2)

    if opts_operaciones:
        kwargs["opts_operaciones"] = opts_operaciones

    request = operation_service_pb2.OperacionRequest(**kwargs)
    print(
        f"[REQUEST ENVIADA]: num1={num1}, op={operacion}, num2={num2}, opts={
            opts_operaciones
        }"
    )

    try:
        response = stub.Operacion(request=request)
        print(f"[EXITO REQUEST] Resultado: {response.result}")
    except grpc.RpcError as e:
        print(f"[ERROR REQUEST] Codigo: {e.code().name}\nDetalles: {e.details()}")


def run_client():
    with grpc.insecure_channel("localhost:8080") as channel:
        stub = operation_service_pb2_grpc.AritmeticaServiceStub(channel=channel)
        print("INICIANDO PRUEBAS DEL CLIENTE gRPC")
        print("=" * 60)

        # 15 + 5 = 20 (valido)
        test_operation(
            stub, "Operacion simple valida: 15 + 5", num1=15.0, operacion="+", num2=5.0
        )

        # 15 + = invalido (sin segundo operando)
        test_operation(
            stub,
            "Operacion incompleta: 15 + (sin segundo operando)",
            num1=15.0,
            operacion="+",
        )

        # 10 / 0 = operacion ilegal (division por cero)
        test_operation(
            stub, "Division por cero: 10 / 0", num1=10.0, operacion="/", num2=0.0
        )

        # Operacion multiple valida
        opts = [
            operation_service_pb2.Operacion(numero="3.0", operacion="*"),
            operation_service_pb2.Operacion(numero="2.0", operacion="+"),
        ]
        test_operation(
            stub,
            "Operacion multiple: 15 + 5 * 3 + 2 = 32",
            num1=15.0,
            operacion="+",
            num2=5.0,
            opts_operaciones=opts,
        )

        # Operador no soportado
        test_operation(
            stub, "Operador no soportado: 15 % 5", num1=15.0, operacion="%", num2=5.0
        )

        # Operacion compleja válida
        opts = [
            operation_service_pb2.Operacion(numero="4.0", operacion="*"),
            operation_service_pb2.Operacion(numero="2.0", operacion="/"),
            operation_service_pb2.Operacion(numero="5.0", operacion="-"),
        ]
        test_operation(
            stub,
            "Operacion compleja: 10 + 6 * 4 / 2 - 5 = 17",
            num1=10.0,
            operacion="+",
            num2=6.0,
            opts_operaciones=opts,
        )

        # Division por 0 en operacion multiple
        opts = [operation_service_pb2.Operacion(numero="0.0", operacion="/")]
        test_operation(
            stub,
            "Division por cero en operacion multiple: 10 + 5 / 0",
            num1=10.0,
            operacion="+",
            num2=5.0,
            opts_operaciones=opts,
        )

        # Numero invalido (string no numerico)
        test_operation(
            stub, "Numero invalido: 'abc' + 5", num1="abc", operacion="+", num2=5.0
        )

        # Operacion adicional sin numero
        opts = [operation_service_pb2.Operacion(numero="", operacion="+")]
        test_operation(
            stub,
            "Operacion adicional sin numero: 10 + 5 + (vacio)",
            num1=10.0,
            operacion="+",
            num2=5.0,
            opts_operaciones=opts,
        )

        # Operacion sin num2 pero si con opts_operaciones (invalido)
        opts = [
            operation_service_pb2.Operacion(numero="5", operacion="+"),
            operation_service_pb2.Operacion(numero="4", operacion="-"),
            operation_service_pb2.Operacion(numero="3", operacion="/"),
        ]
        test_operation(
            stub,
            "Operacion sin numero 2 necesario: 10 + _ + 5 - 9 / 3",
            num1=10.0,
            operacion="+",
            opts_operaciones=opts,
        )
        print("=" * 60 + "\n")


if __name__ == "__main__":
    run_client()
