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
                if isinstance(token, (int, float)):
                    output.append(float(token))
                elif token in self.operators:
                    while (
                        stack
                        and stack[-1] in self.operators
                        and self.operators[stack[-1]] >= self.operators[token]
                    ):
                        output.append(stack.pop())
                    stack.append(token)
                else:
                    print(
                        f"[PARSER] Error: token desconocido '{
                            token
                        }' (operador no soportado)"
                    )
                    return None

            while stack:
                output.append(stack.pop())
            print(f"[PARSER] Infija: {tokens} -> Postfija: {output}")
            return output

        except Exception as e:
            print(f"[PARSER] Excepcion durante el parseo: {e}")
            return None
