import argparse
import grpc
import re
from grpc_tarea.protos import operation_service_pb2, operation_service_pb2_grpc


def parse_expression(expr: str):
    tokens = re.findall(r"([+-/*])|(\d+(?:\.\d+)?)", expr.replace(" ", ""))

    elements = []
    for op, num in tokens:
        if num:
            elements.append(num)
        elif op:
            elements.append(op)

    num1 = elements[0] if len(elements) > 0 else ""
    operacion = elements[1] if len(elements) > 1 else ""
    num2 = elements[2] if len(elements) > 2 else ""

    opts = []
    for i in range(3, len(elements), 2):
        if i + 1 < len(elements):
            opts.append(
                operation_service_pb2.Operacion(
                    operacion=elements[i],
                    numero=str(elements[i + 1]),
                )
            )
        else:
            opts.append(
                operation_service_pb2.Operacion(
                    operacion=elements[i],
                    numero="",
                )
            )

    return str(num1), operacion, str(num2), opts


def send_operation(stub, expr):
    num1, op, num2, opts = parse_expression(expr)

    request = operation_service_pb2.OperacionRequest(
        num1=str(num1), operacion=op, num2=str(num2), opts_operaciones=opts
    )
    print(f"[REQUEST ENVIADA]: {expr}")
    try:
        response = stub.Operacion(request)
        print(f"[RESULTADO] {response.result}\n")
    except grpc.RpcError as e:
        print(f"[ERROR REQUEST] Codigo: {e.code().name}\nDetalles: {e.details()}\n")


def main():
    parser = argparse.ArgumentParser(
        description="Cliente gRPC para operaciones aritmeticas"
    )
    parser.add_argument(
        "expr",
        nargs="?",
        help="Expresion a evaluar",
    )
    args = parser.parse_args()

    with grpc.insecure_channel("localhost:8080") as channel:
        stub = operation_service_pb2_grpc.AritmeticaServiceStub(channel)

        if args.expr:
            send_operation(stub, args.expr)
        else:
            print("Sin expresion, ejecutando pruebas automaticas...\n")
            pruebas = [
                "15 + 5",
                "10 / 0",
                "10 + 5 * 3 + 2",
                "10 + 6 * 4 / 2 - 5",
                "15 % 5",
                "abc + 5",
                "10 + 10 +",
            ]
            for p in pruebas:
                send_operation(stub, p)


if __name__ == "__main__":
    main()
