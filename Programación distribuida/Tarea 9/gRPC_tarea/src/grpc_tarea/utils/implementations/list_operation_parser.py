from grpc_tarea.utils.interfaces.parser import Parser


class ListOperationParser(Parser):
    """
    Parser que convierte una lista en notación infija a notación postfija (RPN)
    usando el algoritmo de Shunting Yard. También valida formato y operadores.
    """

    def __init__(self):
        self.operators = {"+": 1, "-": 1, "*": 2, "/": 2}

    def parse_operation(self, tokens: list):
        """
        Convierte una lista de tokens [num1, op, num2, op, num3, ...]
        a notación postfija. Si hay error de formato, devuelve None.
        """
        if not tokens:
            print("[PARSER] Error: expresión vacía.")
            return None

        if len(tokens) < 3:
            print(
                "[PARSER] Error: expresión demasiado corta. Se necesitan al menos 3 elementos (num op num)."
            )
            return None

        # Validación de formato inicial (num op num op num ...)
        if not self._validate_structure(tokens):
            print(f"[PARSER] Error: formato inválido en {tokens}")
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
            print(f"[PARSER] Excepción durante el parseo: {e}")
            return None

    def _validate_structure(self, tokens):
        """
        Verifica que la expresión tenga alternancia correcta entre número y operador.
        Ej: [15.0, '*', 3.0] es válido, [15.0, '*'] no.
        [15.0, '+', 3.0, '*', 2.0] es válido
        """
        if len(tokens) % 2 == 0:
            print(
                f"[PARSER] Error: número incorrecto de tokens ({
                    len(tokens)
                }). Debe ser impar."
            )
            return False

        expect_number = True
        for i, token in enumerate(tokens):
            if expect_number:
                if not isinstance(token, (int, float)):
                    print(
                        f"[PARSER] Error en posición {
                            i
                        }: se esperaba número, se encontró '{token}' (tipo: {
                            type(token).__name__
                        })"
                    )
                    return False
            else:
                if token not in self.operators:
                    print(
                        f"[PARSER] Error en posición {
                            i
                        }: se esperaba operador (+, -, *, /), se encontró '{token}'"
                    )
                    return False
            expect_number = not expect_number

        # Si termina esperando un número (expect_number == True),
        # significa que el último token fue un operador -> incompleto
        if expect_number:
            print("[PARSER] Error: expresión incompleta (termina con operador)")
            return False

        return True
