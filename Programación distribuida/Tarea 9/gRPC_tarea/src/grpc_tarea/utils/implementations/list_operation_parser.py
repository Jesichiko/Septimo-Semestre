from grpc_tarea.utils.interfaces.parser import Parser

# Usamos como parser el algoritmo shunting yard para pasar una
# lista (ya valida) de operaciones infijas
# a posfijas (que es mas facil de ejecutar/hacer)


class ListOperationParser(Parser):
    def __init__(self):
        self.operators = {"+": 1, "-": 1, "*": 2, "/": 2}

    def parse_operation(self, tokens: list):
        if not tokens:
            print("[PARSER] Error: expresion vacia.")
            return None

        try:
            output = []
            stack = []
            for token in tokens:
                # si el token i es un numero (instancia de int/float)
                if isinstance(token, (int, float)):
                    # lo añadimos al resultado final
                    output.append(float(token))
                elif token in self.operators:  # si es un operador
                    # si la precedencia de los operadores actuales apilados
                    # es mayor o igual a la del token i entonces se sacan
                    # y se añaden a output
                    while (
                        stack
                        and stack[-1] in self.operators
                        and self.operators[stack[-1]] >= self.operators[token]
                    ):
                        output.append(stack.pop())
                    # se añade el token i al stack
                    stack.append(token)
                else:  # si no es operador conocido o numero devolvemos error
                    print(
                        f"[PARSER] Error: token desconocido '{
                            token
                        }' (operador no soportado)"
                    )
                    return None

            while stack:
                # añadimos al final del output los operandos [2, 4, +]
                output.append(stack.pop())
            print(f"[PARSER] Infija: {tokens} -> Postfija: {output}")
            return output

        except Exception as e:
            print(f"[PARSER] Excepcion durante el parseo: {e}")
            return None
