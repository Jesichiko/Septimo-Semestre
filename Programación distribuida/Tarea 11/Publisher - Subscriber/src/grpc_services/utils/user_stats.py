# Estadisticas de los usuarios que enviarons resultados
# Con la addr del usuario se cuentan sus "participaciones" (+1 cada result)
# y se impriminen los usuarios y cuanto han trabajado
# y ademas se suman todos los resultados que se recibieron (suma de todos)

from collections import defaultdict


class UserStats:
    def __init__(self):
        self.user_participations = defaultdict(int)
        self.user_results = defaultdict(list)
        self.total_sum = 0.0

    def addResult(self, user_addr: str, result: float):
        self.user_participations[user_addr] += 1
        self.user_results[user_addr].append(result)
        self.total_sum += result

    def print_statistics(self):
        if not self.user_participations:
            print("No hay usuarios que haya enviado resultados aun")
            return

        print(f"\nTotal de usuarios: {len(self.user_participations)}")
        print(f"Suma total de resultados: {self.total_sum:.2f}")
        print("-" * 60)
        print("\nUsuarios:")
        print("-" * 60)

        sorted_users = sorted(
            self.user_participations.items(), key=lambda x: x[1], reverse=True
        )

        for user_addr, count in sorted_users:
            results = self.user_results[user_addr]
            avg = sum(results) / len(results) if results else 0
            print(f"Usuario: {user_addr}")
            print(f"  - Participaciones: {count}")
            print(f"  - Suma de resultados: {sum(results):.2f}")
            print(f"  - Promedio: {avg:.2f}")
            print()

        print("=" * 60 + "\n")
