import operator
from grpc_tarea.utils.interfaces.execute import ExecuteOperation


class PostfixOperationExecuter(ExecuteOperation):
    @classmethod
    def exec_operation(cls, operations):
        if not operations:
            print("[EXECUTOR] Error: lista vacia")
            return None

        stack = []
        print(f"[EXECUTOR] Evaluando postfija: {operations}")
        try:
            for token in operations:
                if isinstance(token, (int, float)):
                    stack.append(float(token))
                    print(f"  Push {token} -> Stack: {stack}")

                elif token in cls._OPERATORS:
                    if len(stack) < 2:
                        print(
                            f"[EXECUTOR] Error: operador '{
                                token
                            }' sin suficientes operandos"
                        )
                        return None

                    right = stack.pop()
                    left = stack.pop()

                    result = cls._apply_operator(left, token, right)
                    if result is None:
                        return None

                    stack.append(result)
                    print(f"  Op {left} {token} {right} = {result} -> Stack: {stack}")

                else:
                    print(f"[EXECUTOR] Error: token invalido '{token}'")
                    return None

            if len(stack) != 1:
                print(f"[EXECUTOR] Error: stack final invalido {stack}")
                return None

            result = stack[0]
            print(f"[EXECUTOR] Resultado final: {result}\n")
            return result

        except Exception as e:
            print(f"[EXECUTOR] Excepcion inesperada: {e}")
            return None

    # Diccionario de operadores
    _OPERATORS = {
        "+": operator.add,
        "-": operator.sub,
        "*": operator.mul,
        "/": lambda a, b: a / b if b != 0 else None,
        "^": operator.pow,
        "**": operator.pow,
    }

    @classmethod
    def _apply_operator(cls, left, operator_symbol, right):
        try:
            func = cls._OPERATORS.get(operator_symbol)
            if not func:
                print(f"[EXECUTOR] Error: operador no soportado '{operator_symbol}'")
                return None

            result = func(left, right)
            if result is None and operator_symbol in {"/", "%"} and right == 0:
                print("[EXECUTOR] Error: division por cero")
                return None
            return result

        except Exception as e:
            print(f"[EXECUTOR] Excepcion en operador '{operator_symbol}': {e}")
            return None
