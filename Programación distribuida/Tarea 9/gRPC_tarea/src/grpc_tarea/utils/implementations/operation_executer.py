from grpc_tarea.utils.interfaces.execute import ExecuteOperation


class PostfixOperationExecuter(ExecuteOperation):
    """
    Ejecuta operaciones aritméticas en notación postfija (RPN).
    Retorna None si hay error de cálculo o expresión inválida.
    """

    @classmethod
    def exec_operation(cls, operations):
        """
        Evalúa una lista en notación postfija (RPN).

        Args:
            operations (list): Ejemplo [5, 3, 2, '*', '+']

        Returns:
            float | None: Resultado de la operación, o None si hay error.
        """
        if not operations:
            print("[EXECUTOR] Error: lista vacía")
            return None

        stack = []
        operators = {"+", "-", "*", "/", "%", "^", "**"}

        print(f"[EXECUTOR] Evaluando postfija: {operations}")

        try:
            for token in operations:
                if isinstance(token, (int, float)):
                    stack.append(float(token))
                    print(f"  Push {token} -> Stack: {stack}")

                elif token in operators:
                    if len(stack) < 2:
                        print(f"[EXECUTOR] Error: operador '{token}' sin suficientes operandos")
                        return None

                    right = stack.pop()
                    left = stack.pop()

                    result = cls._apply_operator(left, token, right)
                    if result is None:
                        return None  # error dentro del operador

                    stack.append(result)
                    print(f"  Op {left} {token} {right} = {result} -> Stack: {stack}")

                else:
                    print(f"[EXECUTOR] Error: token inválido '{token}'")
                    return None

            if len(stack) != 1:
                print(f"[EXECUTOR] Error: stack final inválido {stack}")
                return None

            result = stack[0]
            print(f"[EXECUTOR] Resultado final: {result}\n")
            return result

        except Exception as e:
            print(f"[EXECUTOR] Excepción inesperada: {e}")
            return None

    @staticmethod
    def _apply_operator(left, operator, right):
        """
        Aplica una operación binaria entre dos operandos.
        Retorna None si hay error (división por cero, operador inválido).
        """
        try:
            if operator == "+":
                return left + right
            elif operator == "-":
                return left - right
            elif operator == "*":
                return left * right
            elif operator == "/":
                if right == 0:
                    print("[EXECUTOR] Error: división por cero")
                    return None
                return left / right
            elif operator == "%":
                if right == 0:
                    print("[EXECUTOR] Error: módulo por cero")
                    return None
                return left % right
            elif operator in {"^", "**"}:
                return left ** right
            else:
                print(f"[EXECUTOR] Error: operador no soportado '{operator}'")
                return None
        except Exception as e:
            print(f"[EXECUTOR] Excepción en operador '{operator}': {e}")
            return None
