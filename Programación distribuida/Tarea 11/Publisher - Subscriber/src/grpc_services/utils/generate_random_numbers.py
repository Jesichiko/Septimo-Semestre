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
                (self.principal_queue, "principal")
                if (r := random.random()) < 0.33
                else (self.second_queue, "secundaria")
                if r < 0.66
                else (self.third_queue, "terciaria")
            ),
            "ponderado": lambda nums: (
                (self.principal_queue, "principal")
                if (r := random.random()) < 0.50
                else (self.second_queue, "secundaria")
                if r < 0.80
                else (self.third_queue, "terciaria")
            ),
            "condicional": lambda nums: (
                (self.principal_queue, "principal")
                if (even_count := sum(1 for n in nums if int(n) % 2 == 0)) == 2
                else (self.second_queue, "secundaria")
                if even_count == 1
                else (self.third_queue, "terciaria")
            ),
        }

        if criteria not in self._CRITERIA:
            raise ValueError(
                f"[GENERADOR NUMS: CRITERIO INVALIDO] Debe ser uno de: {
                    set(self._CRITERIA.keys())
                }"
            )
        self.criteria = criteria

    def _generate_unique_triplet(
        self, available_queues: list[str]
    ) -> tuple[list[int], str]:
        attempts = 0
        while attempts < self.max_attempts:
            num1 = random.randint(1, 1000)
            num2 = random.randint(1, 1000)
            num3 = random.randint(1, 1000)
            triplet_tuple = (num1, num2, num3)

            if triplet_tuple in self.seen:
                attempts += 1
                continue

            # Aplicamos criterio para determinar la cola
            triplet_list = [int(num1), int(num2), int(num3)]
            target_queue, queue_name = self._CRITERIA[self.criteria](triplet_list)

            if queue_name not in available_queues:
                attempts += 1
                continue  # no agregamos el conjunto creado ya que la cola no esta disponible

            self.seen.add(triplet_tuple)
            target_queue.put(triplet_list)
            self.count += 1
            return triplet_list, queue_name

        raise Exception("No se pudo generar tercia unica despues de multiples intentos")

    def getNumbers(self, num_queues: int) -> tuple[list[int], list[str]]:
        with self.lock:
            available_queues = ["principal", "secundaria", "terciaria"]

            if self.count >= self.max_results:
                raise MemoryError(
                    "[GENERADOR NUMS: LIMITE ALCANZADO] ya se generaron todas las tercias posibles"
                )
            if num_queues not in [1, 2]:
                raise ValueError(f"num_queues debe ser 1 o 2, se recibio: {num_queues}")

            # generamos primer conjunto de numeros
            # (siempre se generara al menos uno)
            first_triplet, first_queue = self._generate_unique_triplet(
                available_queues=available_queues
            )

            # Si solo pidio 1 cola retornamos ese conjunto
            if num_queues == 1:
                return first_triplet, [first_queue]

            # Si pidieron 2 colas generamos segundo conjunto de una cola diferente
            available_queues.remove(first_queue)
            second_triplet, second_queue = self._generate_unique_triplet(
                available_queues=available_queues
            )

            # retornamos la combinacion de conjuntos y el nombre de colas
            return first_triplet + second_triplet, [first_queue, second_queue]
