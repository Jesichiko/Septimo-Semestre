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
        if not tokens or len(tokens) < 3:
            print("[PARSER] Error: expresión demasiado corta o vacía.")
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
                    print(f"[PARSER] Error: token desconocido '{token}'")
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
        """
        expect_number = True
        for token in tokens:
            if expect_number:
                if not isinstance(token, (int, float)):
                    return False
            else:
                if token not in self.operators:
                    return False
            expect_number = not expect_number

        # Si termina esperando un número, la expresión está incompleta
        return not expect_number
