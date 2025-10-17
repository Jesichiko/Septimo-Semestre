import pytest
import grpc
from grpc_tarea.protos import operation_service_pb2, operation_service_pb2_grpc


@pytest.fixture(scope="module")
def stub():
    channel = grpc.insecure_channel("localhost:8080")
    yield operation_service_pb2_grpc.AritmeticaServiceStub(channel)
    channel.close()


def send_request(stub, num1, operacion, num2=None, opts=None):
    kwargs = {"num1": str(num1), "operacion": operacion}
    if num2 is not None:
        kwargs["num2"] = str(num2)
    if opts:
        kwargs["opts_operaciones"] = opts

    request = operation_service_pb2.OperacionRequest(**kwargs)
    try:
        response = stub.Operacion(request=request)
        return response.result
    except grpc.RpcError as e:
        return e


def test_operacion_simple_valida(stub):
    result = send_request(stub, 15.0, "+", 5.0)
    assert result == 20.0


def test_operacion_incompleta(stub):
    e = send_request(stub, 15.0, "+")
    assert isinstance(e, grpc.RpcError)
    assert e.code().name == "INVALID_ARGUMENT"
    assert "se requiere num2" in e.details()


def test_division_por_cero(stub):
    e = send_request(stub, 10.0, "/", 0.0)
    assert isinstance(e, grpc.RpcError)
    assert e.code().name == "ABORTED"
    assert "division por 0" in e.details().lower()


def test_operacion_multiple_valida(stub):
    opts = [
        operation_service_pb2.Operacion(numero="3.0", operacion="*"),
        operation_service_pb2.Operacion(numero="2.0", operacion="+"),
    ]
    result = send_request(stub, 15.0, "+", 5.0, opts)
    assert result == 32.0


def test_operador_no_soportado(stub):
    e = send_request(stub, 15.0, "%", 5.0)
    assert isinstance(e, grpc.RpcError)
    assert e.code().name == "INVALID_ARGUMENT"
    assert "parsear" in e.details().lower()


def test_operacion_compleja_valida(stub):
    opts = [
        operation_service_pb2.Operacion(numero="4.0", operacion="*"),
        operation_service_pb2.Operacion(numero="2.0", operacion="/"),
        operation_service_pb2.Operacion(numero="5.0", operacion="-"),
    ]
    result = send_request(stub, 10.0, "+", 6.0, opts)
    assert result == 17.0


def test_division_por_cero_en_multiple(stub):
    opts = [operation_service_pb2.Operacion(numero="0.0", operacion="/")]
    e = send_request(stub, 10.0, "+", 5.0, opts)
    assert isinstance(e, grpc.RpcError)
    assert e.code().name == "ABORTED"


def test_numero_invalido(stub):
    e = send_request(stub, "abc", "+", 5.0)
    assert isinstance(e, grpc.RpcError)
    assert e.code().name == "INVALID_ARGUMENT"
    assert "num1" in e.details().lower()


def test_operacion_adicional_sin_numero(stub):
    opts = [operation_service_pb2.Operacion(numero="", operacion="+")]
    e = send_request(stub, 10.0, "+", 5.0, opts)
    assert isinstance(e, grpc.RpcError)
    assert e.code().name == "INVALID_ARGUMENT"
    assert "vacio" in e.details().lower()


def test_operacion_sin_num2_con_opts(stub):
    opts = [
        operation_service_pb2.Operacion(numero="5", operacion="+"),
        operation_service_pb2.Operacion(numero="4", operacion="-"),
        operation_service_pb2.Operacion(numero="3", operacion="/"),
    ]
    e = send_request(stub, 10.0, "+", None, opts)
    assert isinstance(e, grpc.RpcError)
    assert e.code().name == "INVALID_ARGUMENT"
    assert "se requiere num2" in e.details()
