import random
import threading
from queue import Queue

# Colas publisher del servicio:
# Cola principal, Cola secundaria y Tercera cola


class Generate_Numbers:
    def __init__(self, criteria: str):
        self.principal_queue = Queue()
        self.second_queue = Queue()
        self.third_queue = Queue()
        self.seen = set()
        self.lock = threading.Lock()
        self.count = 0
        self.max_results = 1_000_000
        self.max_attempts = 1000

        # Diccionario de criterios
        self._CRITERIA = {
            "aleatorio": lambda nums: (
                self.principal_queue.put(nums)  # 33%
                if (r := random.random()) < 0.33
                else self.second_queue.put(nums)  # 66%
                if r < 0.66
                else self.third_queue.put(nums)  # 99%
            ),
            "ponderado": lambda nums: (
                self.principal_queue.put(nums)  # 50%
                if (r := random.random()) < 0.50
                else self.second_queue.put(nums)  # 30%
                if r < 0.80
                else self.third_queue.put(nums)  # 20%
            ),
            "condicional": lambda nums: (
                self.principal_queue.put(nums)  # 2 pares
                if (even_count := sum(1 for n in nums if int(n) % 2 == 0)) == 2
                else self.second_queue.put(nums)  # 2 impares
                if even_count == 1
                else self.third_queue.put(nums)  # 0 o 3 pares
            ),
        }

        if criteria not in self._CRITERIA:
            raise ValueError(
                f"[GENERADOR NUMS: CRITERIO INVALIDO] Debe ser uno de: {
                    set(self._CRITERIA.keys())
                }"
            )
        self.criteria = criteria

    def getNumbers(self) -> list[float]:
        with self.lock:
            if self.count >= self.max_results:
                raise MemoryError(
                    "[GENERADOR NUMS: LIMITE ALCANZADO] ya se generaron todas las tercias posibles"
                )

            attempts = 0
            while attempts < self.max_attempts:
                num1 = random.randint(1, 1000)
                num2 = random.randint(1, 1000)
                num3 = random.randint(1, 1000)
                triplet_tuple = (num1, num2, num3)

                if triplet_tuple not in self.seen:
                    self.seen.add(triplet_tuple)
                    triplet_list = [num1, num2, num3]

                    # Aplicamos criterio
                    self._CRITERIA[self.criteria](triplet_list)

                    self.count += 1
                    return triplet_list
                attempts += 1

            raise Exception(
                "No se pudo generar tercia unica despues de multiples intentos"
            )
