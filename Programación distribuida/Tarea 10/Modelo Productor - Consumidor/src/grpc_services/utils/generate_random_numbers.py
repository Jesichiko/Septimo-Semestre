# generamos tercias (num1, num2, num3) con num i random en {1, 1,000}
# y no se deben generar tercias ya repetidas
# si ya no hay posibles tercias entonces retornamos Exception

import random


class Generate_Numbers:
    def __init__(self):
        self.generated_triplets = set()

    def getNumbers(self) -> list[float]:
        attempts = 0

        while attempts < self.max_attempts:
            num1 = random.randint(1, 1000)
            num2 = random.randint(1, 1000)
            num3 = random.randint(1, 1000)

            triplet = (num1, num2, num3)
            if triplet not in self.generated_triplets:
                self.generated_triplets.add(triplet)
                return [float(num1), float(num2), float(num3)]

            if len(self.generated_triplets) == 1000000000:
                raise Exception(
                    "Error: Ya no se pueden crear numeros ya que se terminaron las combinaciones"
                )

    def get_total_generated(self) -> int:
        return len(self.generated_triplets)
