import random
import threading
from queue import Queue


class Generate_Numbers:
    def __init__(self):
        self.generated_triplets = Queue()  # cola de resultados
        self.seen = set()  # Set para verificar unicidad
        self.lock = threading.Lock()  # Lock para evitar race conditions
        self.count = 0
        self.max_results = 1_000_000
        self.max_attempts = 1000

    def getNumbers(self) -> list[float]:
        with self.lock:
            if self.count >= self.max_results:
                raise Exception(
                    "Limite alcanzado: ya se generaron todas las tercias posibles"
                )

            attempts = 0
            while attempts < self.max_attempts:
                # generamos la tercia y la añadimos a la cola
                num1 = random.randint(1, 1000)
                num2 = random.randint(1, 1000)
                num3 = random.randint(1, 1000)

                triplet_tuple = (num1, num2, num3)

                # verificamos unicidad de la tercia creada
                if triplet_tuple not in self.seen:
                    self.seen.add(triplet_tuple)
                    triplet_list = [float(num1), float(num2), float(num3)]
                    self.generated_triplets.put(triplet_list)
                    self.count += 1
                    return triplet_list
                attempts += 1

            raise Exception(
                "No se pudo generar tercia unica despues de multiples intentos"
            )
